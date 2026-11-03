"""Reevaluate frozen scientific artifacts; never fit or replace predictive models.

The separately documented training experiment is not the source of these checks.
All row alignment is by the persisted dataset index, with person keys cross-checked.
"""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import joblib
from scipy.special import logit
from sklearn.base import clone
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.metrics import confusion_matrix
from catboost import Pool
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['conglome', 'vivienda', 'hogar', 'codperso']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load():
    dtype = {k: str for k in [*KEYS, 'ubigeo', 'ano']}
    base = pd.read_csv(ROOT/'data/processed/dataset_enaho_escale_2025.csv', dtype=dtype)
    model = pd.read_csv(ROOT/'data/processed/dataset_modelado_internet_2025.csv', dtype=dtype).set_index('indice_dataset')
    parts = pd.read_csv(ROOT/'reports/tables/partitions.csv', dtype={'conglome': str})
    r = json.loads((ROOT/'reports/results.json').read_text())
    return base, model, parts, r


def aligned_predictions(model, pred, features):
    if not pred.indice.is_unique or not model.index.is_unique:
        raise ValueError('Duplicate prediction or dataset row identifiers')
    return model.loc[pred.indice, features]


def evaluate(phase):
    from run_analysis import metrics, assert_features, SEED
    base, model, parts, r = load()
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def close(name, a, b, atol=1e-9):
        check(name, np.allclose(a, b, atol=atol, rtol=1e-8, equal_nan=True))

    train = model.loc[parts.loc[parts.particion.eq('desarrollo'), 'indice']]
    test = model.loc[parts.loc[parts.particion.eq('prueba'), 'indice']]
    features = r['features']
    detail = {}
    if phase == 'dataset':
        reference=ROOT/'docs/SCIENTIFIC_REFERENCE.json'
        if reference.exists():
            for path,digest in json.loads(reference.read_text())['frozen_sha256'].items():
                check('frozen_'+path,sha(ROOT/path)==digest)
        check('dataset_sha256', sha(ROOT/'data/processed/dataset_enaho_escale_2025.csv') == r['dataset_sha256'])
        check('analysis_code_sha256', hashlib.sha256((ROOT/'src/run_analysis.py').read_bytes()+(ROOT/'src/nonlinear_shap.py').read_bytes()).hexdigest() == r['analysis_code_sha256'])
        check('unique_person_keys', not base.duplicated(KEYS).any())
        check('unique_partition_indices', parts.indice.is_unique and set(parts.indice) == set(model.index))
        check('group_labels_aligned', np.array_equal(parts.conglome.to_numpy(), model.loc[parts.indice, 'conglome'].to_numpy()))
        check('no_group_overlap', set(train.conglome).isdisjoint(test.conglome))
        a, b = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=SEED).split(model, groups=model.conglome))
        check('train_order_seed42', np.array_equal(model.iloc[a].index, train.index))
        check('test_order_seed42', np.array_equal(model.iloc[b].index, test.index))
        original = base.loc[model.index]
        check('person_keys_aligned', np.array_equal(original[KEYS].to_numpy(), model[KEYS].to_numpy()))
        check('population_rules', original.edad.between(6,17).all() and original.residente_habitual.eq(1).all() and original.p306.eq(1).all() and original.p307.eq(1).all() and original.p308a.isin([2,3]).all() and not original.p307d.eq(1).any() and original.p314a.isin([1,2]).all())
        close('target_recomputed', original.p314a.eq(2).astype(int), model.target_internet)
        close('individual_population_weight', original.peso_persona, model.peso_persona)
        check('weights_positive', model.peso_persona.gt(0).all())
        for source, target in [('ingreso_pc_mensual','log_ingreso_pc'),('gasto_pc_mensual','log_gasto_pc')]:
            close('transform_'+target, np.log1p(original[source].where(original[source]>=0)), model[target])
        for f in set(features)-{'log_ingreso_pc','log_gasto_pc'}:
            close('feature_'+f, original[f], model[f])
        assert_features(features)
        folds = pd.read_csv(ROOT/'reports/tables/cv_assignments.csv')
        for i, (a,b) in enumerate(GroupKFold(5).split(train, groups=train.conglome),1):
            check('fold_membership_'+str(i), set(folds.loc[folds.fold.eq(i),'indice']) == set(train.iloc[b].index))
            check('fold_group_isolation_'+str(i), set(train.iloc[a].conglome).isdisjoint(train.iloc[b].conglome))
        detail = {'n_integrated':len(base),'n_model':len(model),'n_train':len(train),'n_test':len(test),'group_overlap':0,'dataset_sha256':r['dataset_sha256']}
    elif phase == 'classification':
        best = joblib.load(ROOT/'models/best_model.joblib')
        allmodels = joblib.load(ROOT/'models/all_models.joblib')
        pred = pd.read_csv(ROOT/'reports/tables/test_predictions.csv', dtype={'conglome':str})
        oof = pd.read_csv(ROOT/'reports/tables/oof_predictions.csv')
        check('test_prediction_order', np.array_equal(pred.indice, test.index))
        check('oof_development_order', np.array_equal(oof.indice, train.index))
        close('test_target', pred.y, test.target_internet)
        close('test_weights', pred.peso, test.peso_persona)
        close('oof_target', oof.y, train.target_internet)
        close('oof_weights', oof.peso, train.peso_persona)
        check('features_and_threshold', best['features']==features and best['threshold']==r['threshold']==.5)
        check('target_unchanged', best['target']=='target_internet')
        cv = pd.read_csv(ROOT/'reports/tables/model_comparison_cv.csv')
        check('winner_selected_in_development', cv.iloc[0].modelo==best['winner']==r['supervised']['winner']=='CatBoost')
        computed=[]
        for row in r['supervised']['test']:
            name=row['modelo'];pipe=allmodels['pipelines'][name];cal=allmodels['calibrators'][name]
            x=aligned_predictions(model,pred,features)
            check('preprocess_columns_'+name, list(pipe.named_steps['preprocess'].feature_names_in_)==features)
            raw=pipe.predict_proba(x)[:,1]
            p=cal.predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
            close('saved_predictions_'+name, p, pred[name],atol=1e-10)
            refit=clone(cal).fit(logit(np.clip(oof[name].to_numpy(),1e-6,1-1e-6)).reshape(-1,1),oof.y,sample_weight=oof.peso/oof.peso.mean())
            close('calibration_oof_coefficient_'+name, refit.coef_,cal.coef_)
            close('calibration_oof_intercept_'+name, refit.intercept_,cal.intercept_)
            weighted=metrics(pred.y,p,pred.peso)
            for k,v in weighted.items():close('weighted_'+name+'_'+k,v,row[k])
            for k,v in metrics(pred.y,p,None).items():close('unweighted_'+name+'_'+k,v,row[k+'_no_ponderado'])
            computed.append({'modelo':name,**weighted})
        raw=best['pipeline'].predict_proba(test[features])[:,1]
        p=best['calibrator'].predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
        close('best_bundle_predictions', p,pred[best['winner']])
        close('confusion_counts',confusion_matrix(pred.y,p>=.5),r['supervised']['confusion_counts'])
        detail={'winner':best['winner'],'threshold':.5,'metrics':computed,'calibration':'Reajustada sólo sobre OOF de desarrollo para verificar coeficientes; ningún modelo predictivo se entrena ni se reemplaza.'}
    elif phase == 'clustering':
        c=joblib.load(ROOT/'models/clustering.joblib');z=c['preprocess'].transform(train[c['features']]);labels=c['model'].predict(z)
        selected=r['clustering']['selected'];assign=pd.read_csv(ROOT/'reports/tables/cluster_assignments.csv').set_index('indice')
        check('saved_gmm_k2', type(c['model']).__name__=='GaussianMixture' and c['model'].n_components==selected['k']==2)
        close('train_assignments',labels,assign.loc[train.index,'cluster'])
        close('test_assignments',c['model'].predict(c['preprocess'].transform(test[c['features']])),assign.loc[test.index,'cluster'])
        geometric={'silueta':silhouette_score(z,labels,sample_size=min(2500,len(z)),random_state=SEED),'davies_bouldin':davies_bouldin_score(z,labels),'calinski_harabasz':calinski_harabasz_score(z,labels)}
        for k,v in geometric.items():close('geometry_'+k,v,selected[k])
        close('imputer_development_only',c['preprocess'].named_steps['impute'].statistics_,train[c['features']].median())
        for profile in r['clustering']['profiles']:
            mask=labels==profile['cluster'];w=train.peso_persona.to_numpy()[mask]
            check('profile_size_'+str(profile['cluster']),int(mask.sum())==profile['n'])
            close('profile_nonuse_'+str(profile['cluster']),np.average(train.target_internet.to_numpy()[mask],weights=w),profile['no_uso_ponderado'])
        detail={'selected':{'metodo':'GMM','k':2,**geometric},'profiles':r['clustering']['profiles'],'access_ablation':r['clustering']['access_ablation']}
    elif phase == 'shap':
        import shap
        best=joblib.load(ROOT/'models/best_model.joblib');ct=best['pipeline'].named_steps['preprocess'];est=best['pipeline'].named_steps['model']
        raw=best['pipeline'].predict_proba(test[features])[:,1];p=best['calibrator'].predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1];y=test.target_internet.to_numpy()
        high=np.flatnonzero((y==1)&(p>=.5));low=np.flatnonzero((y==0)&(p<.5));high=high[np.argmax(p[high])];low=low[np.argmin(p[low])]
        ids=np.unique(np.r_[np.random.default_rng(SEED).choice(len(test),min(600,len(test)),replace=False),high,low]);z=ct.transform(test.iloc[ids][features]);values=est.get_feature_importance(Pool(z),type='ShapValues')
        sv=values[:,:-1];basevalues=values[:,-1];margin=est.predict(z,prediction_type='RawFormulaVal');residual=float(np.max(np.abs(basevalues+sv.sum(1)-margin)))
        check('catboost_shap_additivity',residual<1e-10)
        def origins(transform):
            return np.array([max([f for f in features if n.split('__',1)[1]==f or n.split('__',1)[1].startswith(f+'_')],key=len) for n in transform.get_feature_names_out()])
        origin=origins(ct);agg=np.column_stack([sv[:,origin==f].sum(1) for f in features]);importance=np.abs(agg).mean(0)
        expected={x['variable']:x['mean_abs_shap'] for x in r['shap']['importance']}
        close('catboost_shap_importance',importance,[expected[f] for f in features])
        check('catboost_shap_sample',len(ids)==r['shap']['n_explained'])
        for case,row in zip(r['shap']['cases'],[high,low]):
            pos=int(np.flatnonzero(ids==row)[0]);close('case_probability_'+case['caso'],p[row],case['probabilidad_calibrada']);close('case_score_'+case['caso'],margin[pos],case['score_modelo'])
            for term in case['top_contribuciones']:close('case_'+case['caso']+'_'+term['variable'],agg[pos,features.index(term['variable'])],term['shap'])
        allmodels=joblib.load(ROOT/'models/all_models.joblib');pipe=allmodels['pipelines']['XGBoost'];ct=pipe.named_steps['preprocess'];est=pipe.named_steps['model'];ids=np.random.default_rng(SEED).choice(len(test),min(180,len(test)),replace=False);z=ct.transform(test.iloc[ids][features]);ex=shap.TreeExplainer(est,feature_perturbation='tree_path_dependent',model_output='raw');iv=np.asarray(ex.shap_interaction_values(z));sv=np.asarray(ex.shap_values(z));margin=est.predict(z,output_margin=True)
        residual_xgb=float(np.max(np.abs(float(np.asarray(ex.expected_value).ravel()[0])+iv.sum((1,2))-margin)))
        check('xgboost_interaction_additivity',residual_xgb<1e-5)
        check('xgboost_interaction_rows',np.max(np.abs(iv.sum(2)-sv))<1e-5)
        origin=origins(ct)
        for i,pair in enumerate(r['nonlinear_shap']['pairs']):
            a=np.flatnonzero(origin==pair['variable_1']);b=np.flatnonzero(origin==pair['variable_2']);actual=np.abs(2*iv[:,a,:][:,:,b].sum((1,2))).mean();close('xgboost_pair_'+str(i),actual,pair['mean_abs_pair_contribution'],atol=1e-7)
        detail={'model':'CatBoost','n_explained':len(values),'units':'log-odds antes de calibrar','max_additivity_residual':residual,'importance':[{'variable':f,'mean_abs_shap':float(v)} for f,v in zip(features,importance)],'complementary_model':'XGBoost','xgboost_n_explained':len(iv),'xgboost_residual':residual_xgb}
    else:
        raise ValueError(phase)
    return {'phase':phase,'status':'passed','executed_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'detail':detail,'historical_test_warning':r['historical_test_warning']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['dataset','classification','clustering','shap','all'],default='all');args=parser.parse_args()
    out=ROOT/'reports/scientific_audit';out.mkdir(exist_ok=True)
    with threadpool_limits(limits=4):
        for phase in (['dataset','classification','clustering','shap'] if args.phase=='all' else [args.phase]):
            result=evaluate(phase);(out/(phase+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(phase,result['status'],len(result['checks']))


if __name__=='__main__':main()
