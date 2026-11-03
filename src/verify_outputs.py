"""Verificación independiente; informa solo controles realmente ejecutados."""
from pathlib import Path
import argparse,json,hashlib,platform,subprocess,sys
import os
from datetime import datetime,timezone
from importlib.metadata import version
import numpy as np
import pandas as pd
import joblib
from scipy.special import logit
from sklearn.model_selection import GroupShuffleSplit,GroupKFold
from sklearn.metrics import confusion_matrix
from pypdf import PdfReader
from run_analysis import metrics,assert_features,SEED,models_config
ROOT=Path(__file__).resolve().parents[1]

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--skip-pdf',action='store_true');ap.add_argument('--skip-notebooks',action='store_true');args=ap.parse_args()
    checks=[];warnings=[]
    def check(name,condition,detail=''):
        checks.append({'name':name,'passed':bool(condition),'detail':detail})
    r=json.loads((ROOT/'reports/results.json').read_text());audit=json.loads((ROOT/'reports/tables/data_audit.json').read_text())
    manifest=json.loads((ROOT/'data/raw/source_manifest.json').read_text())
    sources=manifest.get('archives',[])
    if manifest.get('files'):
        for item in manifest['files']:
            path=ROOT/'data/raw'/item['path'];check('raw_'+item['module'],path.exists() and sha(path)==item['sha256'])
    for src in ([] if manifest.get('files') else sources):
        text=src['path'].replace('${SOURCE_DIR}',os.environ.get('IA_SOURCE_DIR',str(Path.home()/'Downloads/DocenteMaterial'))).replace('${ANNUAL_DIR}',os.environ.get('IA_ANNUAL_DIR',str(Path.home()/'Downloads')))
        p=Path(os.path.expandvars(text));check('source_'+p.name,p.exists() and sha(p)==src['sha256'],'SHA256 original')
    basepath=ROOT/'data/processed/dataset_enaho_escale_2025.csv'
    check('dataset_hash',sha(basepath)==r['dataset_sha256']==audit['output']['sha256'])
    check('analysis_code_provenance',r['analysis_code_sha256']==hashlib.sha256((ROOT/'src/run_analysis.py').read_bytes()+(ROOT/'src/nonlinear_shap.py').read_bytes()).hexdigest())
    check('raw_eda',len(pd.read_csv(ROOT/'reports/tables/raw_eda_variables.csv'))>50 and (ROOT/'reports/figures/raw_eda.png').exists())
    check('padlocal_unique_and_no_multiplication',audit['escale']['padlocal_unique_codlocal'] and audit['escale']['services_before_local_join']==audit['escale']['services_after_local_join'])
    check('padlocal_geographic_quarantine',audit['escale']['geographic_conflicting_services']==1 and audit['escale']['area_conflicting_services']==0)
    measurement=json.loads((ROOT/'reports/tables/target_measurement_audit.json').read_text())
    check('target_skips_and_universe',all(measurement['checks'].values()) and measurement['source_sha256']==sha(basepath))
    keys=['conglome','vivienda','hogar','codperso','ubigeo'];dtype={k:str for k in keys}
    base=pd.read_csv(basepath,dtype=dtype);model=pd.read_csv(ROOT/'data/processed/dataset_modelado_internet_2025.csv',dtype=dtype)
    check('unique_person_keys',not base.duplicated(keys[:4]).any())
    for k,width in zip(keys,[6,3,2,2,6]):check('key_width_'+k,base[k].str.fullmatch(r'\d{'+str(width)+'}').all())
    check('age_residency',base.edad.between(6,17).all() and base.residente_habitual.eq(1).all())
    for name,m in audit['merges'].items():check('merge_'+name,m['left_rows']==m['output_rows'] and not m['row_multiplication'])
    for name in ['dataset_enaho_escale_2025','dataset_modelado_2025']:
        pq=pd.read_parquet(ROOT/f'data/processed/{name}.parquet')
        csv=base if name=='dataset_enaho_escale_2025' else model
        check('parquet_'+name,len(pq)==len(csv) and set(pq)==set(csv))
        for c in set(pq).intersection(keys):check('parquet_text_'+name+'_'+c,pq[c].map(lambda v:isinstance(v,str)).all())
    parts=pd.read_csv(ROOT/'reports/tables/partitions.csv',dtype={'conglome':str})
    train=parts[parts.particion.eq('desarrollo')];test=parts[parts.particion.eq('prueba')]
    check('zero_group_overlap',set(train.conglome).isdisjoint(set(test.conglome)))
    check('partition_counts',len(parts)==r['n_eligible']==len(model) and len(train)==r['n_train'] and len(test)==r['n_test'] and parts.indice.is_unique)
    cohort=base.loc[parts.indice]
    check('population_rules',cohort.p306.eq(1).all() and cohort.p307.eq(1).all() and cohort.p308a.isin([2,3]).all() and (~cohort.p307d.eq(1)).all() and cohort.p314a.isin([1,2]).all())
    a,b=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(model,groups=model.conglome))
    check('seed42_partition_reproduction',set(model.iloc[a].indice_dataset)==set(train.indice) and set(model.iloc[b].indice_dataset)==set(test.indice))
    folds=pd.read_csv(ROOT/'reports/tables/cv_assignments.csv')
    trainmodel=model.set_index('indice_dataset').loc[train.indice]
    for fold,(_,validation) in enumerate(GroupKFold(5).split(trainmodel,groups=trainmodel.conglome),1):
        expected=set(trainmodel.index[validation]);observed=set(folds.loc[folds.fold.eq(fold),'indice'])
        check('fold'+str(fold)+'_reproduction',expected==observed)
        check('fold'+str(fold)+'_group_isolation',set(trainmodel.loc[list(expected),'conglome']).isdisjoint(set(trainmodel.drop(index=list(expected)).conglome)))
    try:assert_features(r['features']);safe=True
    except ValueError:safe=False
    check('forbidden_features',safe)
    cv=pd.read_csv(ROOT/'reports/tables/model_comparison_cv.csv');search=pd.read_csv(ROOT/'reports/tables/model_search.csv')
    check('winner_from_cv',len(cv)==4 and cv.iloc[0].modelo==r['supervised']['winner'] and cv.iloc[0].ap_cv_media==cv.ap_cv_media.max())
    check('cv_fits',len(pd.read_csv(ROOT/'reports/tables/cv_folds.csv'))==len(search)*5==sum(len(c) for _,_,c in models_config())*5)
    sensitivity=pd.read_csv(ROOT/'reports/tables/weight_sensitivity.csv');check('weight_sensitivity',len(sensitivity)==16 and sensitivity.estrategia.nunique()==4)
    pred=pd.read_csv(ROOT/'reports/tables/test_predictions.csv',dtype={'conglome':str});check('test_rows',set(pred.indice)==set(test.indice))
    check('target_recomputed',np.array_equal(base.loc[pred.indice,'p314a'].eq(2).to_numpy(dtype=int),pred.y.to_numpy()))
    for row in r['supervised']['test']:
        p=pred[row['modelo']];check('probability_'+row['modelo'],p.between(0,1).all())
        for weighted,w in [(True,pred.peso),(False,None)]:
            for k,v in metrics(pred.y,p,w).items():
                key=k if weighted else k+'_no_ponderado';check('metric_'+row['modelo']+'_'+key,np.isclose(v,row[key],rtol=1e-8,atol=1e-10))
    best=joblib.load(ROOT/'models/best_model.joblib');ordered=model.set_index('indice_dataset').loc[pred.indice]
    raw=best['pipeline'].predict_proba(ordered[best['features']])[:,1]
    p=best['calibrator'].predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
    check('saved_model_predictions',np.allclose(p,pred[best['winner']],atol=1e-10))
    check('confusion_recomputed',np.array_equal(confusion_matrix(pred.y,p>=.5),r['supervised']['confusion_counts']))
    check('shap_additivity',r['shap']['max_additivity_residual']<.01)
    check('nonlinear_shap_additivity',r['nonlinear_shap']['max_additivity_residual']<.01 and r['nonlinear_shap']['max_interaction_row_residual']<.01)
    check('two_correct_cases',len(r['shap']['cases'])==2 and all((x['probabilidad_calibrada']>=.5)==bool(x['y']) for x in r['shap']['cases']) and {x['y'] for x in r['shap']['cases']}=={0,1})
    check('clustering_grid',len(pd.read_csv(ROOT/'reports/tables/clustering_comparison.csv'))==10)
    check('clustering_stability',len(pd.read_csv(ROOT/'reports/tables/clustering_stability.csv'))==6)
    for name in ['eda','clustering','silhouette','model_curves','confusion_matrix','shap_beeswarm','shap_dependence_1','shap_dependence_2','shap_waterfall_alto','shap_waterfall_bajo','shap_nonlinear_dependence_1','shap_nonlinear_dependence_2','shap_interaction_1','shap_interaction_2']:
        p=ROOT/f'reports/figures/{name}.png';check('figure_'+name,p.exists() and p.stat().st_size>1000)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,text=True,capture_output=True)
    (ROOT/'reports/tests.log').write_text(tests.stdout+tests.stderr)
    check('unit_tests',tests.returncode==0,tests.stderr[-4000:])
    nb=ROOT/'reports/notebook_execution.json'
    if args.skip_notebooks:
        warnings.append('Notebooks not rerun in this isolated source-recovery validation; scripts executed directly.')
    elif nb.exists():
        executions=json.loads(nb.read_text());check('five_notebooks_executed',len(executions)==5 and all(x['status']=='passed' for x in executions))
        for x in executions:
            check('notebook_hash_'+Path(x['notebook']).stem,sha(ROOT/x['notebook'])==x['sha256'])
            notebook=json.loads((ROOT/x['notebook']).read_text())
            check('notebook_outputs_'+Path(x['notebook']).stem,all(c.get('execution_count') is not None and not any(o.get('output_type')=='error' for o in c.get('outputs',[])) for c in notebook['cells'] if c['cell_type']=='code'))
            check('notebook_inputs_'+Path(x['notebook']).stem,all(sha(ROOT/p)==h for p,h in notebook['metadata'].get('scientific_inputs',{}).items()) and bool(notebook['metadata'].get('scientific_inputs')))
    else:check('five_notebooks_executed',False,'No hay registro de ejecución')
    if not args.skip_pdf:
        pdf=PdfReader(ROOT/'output/pdf/Informe_U2_Brecha_Digital_2025.pdf');text='\n'.join(p.extract_text() for p in pdf.pages)
        check('paper_pages',4<=len(pdf.pages)<=6)
        check('paper_content',all(x in text for x in ['SHAP','ENAHO','ESCALE','GroupKFold']) and '\ufffd' not in text)
        winning=next(x for x in r['supervised']['test'] if x['seleccionado_cv'])
        check('paper_definitive_metrics',all(f'{winning[k]:.3f}' in text for k in ['roc_auc','average_precision','f1_macro']) and f"{r['clustering']['selected']['silueta']:.3f}" in text)
    from scientific_audit import evaluate
    from threadpoolctl import threadpool_limits
    definitive_scope=audit.get('source_mode')!='teacher'
    if definitive_scope:
        with threadpool_limits(limits=4):
            for phase in ['dataset','classification','clustering','shap']:
                current=evaluate(phase)
                for c in current['checks']:check('scientific_'+phase+'_'+c['name'],c['passed'])
    else:
        warnings.append('Separate instructor-order experiment: the frozen annual scientific-reference checks are not applicable; this result does not certify equality to the definitive models.')
    warnings += [r['historical_test_warning'],'El objetivo mide no uso reciente; no mide directamente competencias digitales.','Inferencia ponderada de cohorte, no estimación oficial nacional; bootstrap no incorpora todo el diseño de encuesta.']
    private_names={'01_Revision_de_resultados.ipynb','test_predictions.csv','oof_predictions.csv','partitions.csv','cv_assignments.csv','cluster_assignments.csv'}
    paths=[p for folder in ['models','notebooks','output/pdf','data/processed','reports/figures','reports/tables'] for p in (ROOT/folder).glob('*') if p.is_file() and p.name not in private_names]
    paths += [ROOT/p for p in ['reports/results.json','reports/public_summary.json','reports/notebook_execution.json','docs/SCIENTIFIC_REFERENCE.json','docs/SCIENTIFIC_REPRODUCTION.json','docs/SOURCE_ORDER_AUDIT.json'] if (ROOT/p).exists()]
    paths += [p for folder in ['src','scripts','tests','docs'] for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in {'.py','.md','.json'}]
    paths += [ROOT/p for p in ['README.md','requirements.txt','.gitignore','data/raw/source_manifest.json','data/raw/teacher_source_manifest.json','data/raw/download_manifest.json']]
    artifacts=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(paths))]
    final={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'status':'passed' if all(c['passed'] for c in checks) else 'failed',
      'software':{**r['software'],**{p:version(p) for p in ['pyarrow','reportlab','pypdf','nbformat','nbclient','ipykernel']}},'python':platform.python_version(),'sources':sources,'configuration':{'seed':SEED,'run_signature':r['run_signature'],'features':r['features'],'weight_strategies':r['supervised']['weight_strategies'],'winner':best['winner'],'threshold':.5},
      'n_data':len(base),'n_model':len(model),'n_train':len(train),'n_test':len(test),'groups_train':train.conglome.nunique(),'groups_test':test.conglome.nunique(),'group_overlap':len(set(train.conglome)&set(test.conglome)),
      'metrics':r['supervised']['test'],'checks':checks,'passed_checks':sum(c['passed'] for c in checks),'failed_checks':[c for c in checks if not c['passed']],
      'warnings':warnings,'artifacts':artifacts,'pdf_checked':not args.skip_pdf,
      'inventory_scope':'Current publication artifacts; individual prediction/fold traces remain local and are regenerated by isolated training. Historical ignored notebooks are excluded.',
      'scientific_reference':'docs/SCIENTIFIC_REFERENCE.json',
      'scientific_reference_scope':'definitive_annual_reference' if definitive_scope else 'separate_instructor_order_experiment',
      'raw_source_role':'Instructor recovery sources; the definitive annual-layout dataset and its separate source-equivalence audit are documented in docs/SOURCE_ORDER_AUDIT.json.'}
    for name in ['final_verification.json','verification.json']:(ROOT/'reports'/name).write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:final[k] for k in ['status','passed_checks','failed_checks','n_data','n_model','group_overlap']},ensure_ascii=False,indent=2))
    if final['status']!='passed':raise SystemExit(1)
if __name__=='__main__':main()
