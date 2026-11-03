"""EDA, clustering, validación agrupada, prueba y SHAP. Ejecutar desde la raíz.

Las decisiones y los hiperparámetros se seleccionan exclusivamente en desarrollo.
La prueba se reserva por conglomerado. Las explicaciones describen el score previo
a una calibración sigmoide aprendida de predicciones fuera de fold de desarrollo.
"""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'tmp/matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT/'tmp/cache'))
os.environ.setdefault('OMP_NUM_THREADS', '4')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '4')
import argparse, json, warnings, platform, time, hashlib
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from sklearn.base import clone
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.metrics import (roc_auc_score, average_precision_score, precision_recall_curve,
    roc_curve, auc, f1_score, confusion_matrix, precision_score, recall_score,
    brier_score_loss, silhouette_score, silhouette_samples, davies_bouldin_score,
    calinski_harabasz_score, adjusted_rand_score)
from xgboost import XGBClassifier
from catboost import CatBoostClassifier, Pool
import shap, joblib
from scipy.special import expit, logit
from threadpoolctl import threadpool_limits

SEED=42
FIG=ROOT/'reports/figures'; TAB=ROOT/'reports/tables'
for d in [FIG,TAB,ROOT/'models']:d.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
 'axes.spines.right':False,'figure.dpi':120,'savefig.dpi':300,'axes.titleweight':'bold'})
COLORS=['#117c83','#db8e39','#6654a1','#4575a5','#a64d63','#7b8744']
LABELS={'sexo':'Sexo','lengua_materna':'Lengua materna','rural':'Área rural',
 'pobreza':'Pobreza','electricidad':'Electricidad','internet_hogar':'Internet en hogar',
 'altitud':'Altitud','log_ingreso_pc':'Log ingreso per cápita','log_gasto_pc':'Log gasto per cápita',
 'ratio_alumnos_docente':'Alumnos/docente distrital','prop_publicas':'Proporción públicas',
 'escale_coincide':'Cobertura ESCALE','edad':'Edad'}
CLASS_NAMES=['Usó internet','No usó internet']

def dump(path,obj):
    def conv(v):
        if isinstance(v,np.generic):return v.item()
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,Path):return str(v)
        raise TypeError(str(type(v)))
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=conv),encoding='utf-8')

def savefig(name):
    plt.savefig(FIG/name,bbox_inches='tight',facecolor='white');plt.close()

def wm(x,w):
    x=np.asarray(x,dtype=float); w=np.asarray(w,dtype=float)
    ok=np.isfinite(x)&np.isfinite(w)&(w>0)
    return float(np.average(x[ok],weights=w[ok])) if ok.any() else np.nan

def metrics(y,p,w):
    tn,fp,fn,tp=confusion_matrix(y,np.asarray(p)>=.5,sample_weight=w,labels=[0,1]).ravel()
    z=(p>=.5).astype(int);pr,re,_=precision_recall_curve(y,p,sample_weight=w)
    return {'roc_auc':roc_auc_score(y,p,sample_weight=w),
      'average_precision':average_precision_score(y,p,sample_weight=w),
      'pr_auc_trapezoidal':auc(re,pr),'f1_macro':f1_score(y,z,average='macro',sample_weight=w),
      'precision':precision_score(y,z,sample_weight=w,zero_division=0),
      'recall':recall_score(y,z,sample_weight=w,zero_division=0),
      'brier':brier_score_loss(y,p,sample_weight=w),
      'specificity':float(tn/(tn+fp)) if tn+fp else float('nan')}

def fitweights(y,w,strategy="population_class"):
    """Peso poblacional y balance de clase calculado sólo en el fold de ajuste."""
    w=np.array(w,dtype=float) if strategy in {"population","population_class"} else np.ones(len(y)); totals=np.bincount(y,weights=w,minlength=2)
    assert (totals>0).all()
    result=w*(totals.sum()/(2*totals))[y] if strategy in {"class","population_class"} else w
    return result/result.mean()

def prepare_targets(df):
    age=pd.to_numeric(df.edad,errors='coerce')
    level=pd.to_numeric(df.p308a,errors='coerce')
    year=pd.to_numeric(df.p308b,errors='coerce')
    grade=pd.to_numeric(df.p308c,errors='coerce')
    enrolled=pd.to_numeric(df.p306,errors='coerce').eq(1)
    attends=pd.to_numeric(df.p307,errors='coerce').eq(1)
    internet=pd.to_numeric(df.p314a,errors='coerce')
    valid_grade=(level.eq(2)&grade.between(1,6))|(level.eq(3)&year.between(1,5))
    normative=np.where(level.eq(2),grade+5,np.where(level.eq(3),year+11,np.nan))
    gap=age-normative
    # INEI, Documento metodológico Indicadores de Educación: edad actual.
    # No corresponde al indicador ESCALE/SIAGIE de edad al 31 de marzo.
    df['edad_normativa']=normative;df['desfase_edad_grado']=gap
    ceba=pd.to_numeric(df.p307d,errors='coerce').eq(1)
    valid=enrolled&attends&valid_grade&~ceba&age.between(6,17)
    df['target_rezago']=np.where(valid,(gap>=1).astype(int),np.nan)
    df['target_rezago_2']=np.where(valid,(gap>=2).astype(int),np.nan)
    vi=enrolled&attends&level.isin([2,3])&~ceba&internet.isin([1,2])&age.between(6,17)
    df['target_internet']=np.where(vi,internet.eq(2).astype(int),np.nan)
    flow=[];mask=pd.Series(True,index=df.index);previous=len(df)
    rules=[('Base integrada residentes6-17',mask.copy()),('Edad6-17',age.between(6,17)),
      ('Matriculados P306=1',enrolled),('Asistentes P307=1',attends),
      ('Primaria/secundaria P308A2/3',level.isin([2,3])),('Sin CEBA declarado',~ceba),
      ('Respuesta válida P314A1/2',internet.isin([1,2])),('Peso individual positivo',pd.to_numeric(df.peso_persona,errors='coerce').gt(0))]
    for step,rule in rules:
        mask &= rule;count=int(mask.sum());flow.append({'etapa':step,'n':count,'excluidos_en_etapa':previous-count});previous=count
    pd.DataFrame(flow).to_csv(TAB/'population_flow_model.csv',index=False)
    comparison=[]
    for name in ['target_rezago','target_rezago_2','target_internet']:
        sub=df[df[name].notna()];w=pd.to_numeric(sub.peso_persona,errors='coerce')
        comparison.append({'objetivo':name,'n_validos':len(sub),'n_positivos':int(sub[name].sum()),
          'n_negativos':int(len(sub)-sub[name].sum()),'prevalencia_muestral':sub[name].mean(),
          'prevalencia_ponderada':wm(sub[name],w),'conglomerados':sub.conglome.nunique()})
    pd.DataFrame(comparison).to_csv(TAB/'target_comparison.csv',index=False)
    bymonth=df.loc[valid].groupby('mes').agg(n=('target_rezago','size'),
        desfase_1=('target_rezago','mean'),desfase_2=('target_rezago_2','mean'))
    bymonth.to_csv(TAB/'target_rezago_by_month.csv')
    return df,comparison

def eda(df,features,y,w):
    missing=df[features].isna().mean().sort_values(ascending=False)
    missing.rename('proporcion_faltante').to_csv(TAB/'missing_train.csv')
    df[features].describe(include='all').to_csv(TAB/'descriptive_train.csv')
    rows=[]
    groups={'Área':np.where(df.rural.eq(1),'Rural','Urbana'),
      'Pobreza':df.pobreza.map({1:'Extrema',2:'No extrema',3:'No pobre'}).fillna('Sin dato'),
      'Lengua':np.select([df.lengua_materna.isin([1,2]),df.lengua_materna.eq(4)],
                        ['Quechua/Aimara','Castellano'],default='Otras/sin dato')}
    for key,vals in groups.items():
        vals=np.array(vals)
        for val in np.unique(vals):
            m=vals==val;rows.append({'variable':key,'grupo':val,'n':int(m.sum()),'prevalencia':wm(y[m],w[m])})
    pd.DataFrame(rows).to_csv(TAB/'eda_subgroups_train.csv',index=False)
    fig,axs=plt.subplots(2,2,figsize=(10,6.2))
    axs[0,0].hist(df.edad,bins=np.arange(5.5,18.5),color=COLORS[0],rwidth=.85)
    axs[0,0].set(xlabel='Edad actual',ylabel='Personas',title='Desarrollo: distribución de edades')
    for ax,key in zip([axs[0,1],axs[1,0]],['Área','Pobreza']):
        sub=[r for r in rows if r['variable']==key]
        ax.bar([r['grupo'] for r in sub],[100*r['prevalencia'] for r in sub],color=COLORS[:len(sub)])
        ax.set(ylabel='No uso de internet ponderado (%)',title=key);ax.tick_params(axis='x',labelsize=9)
    show=missing.head(6).iloc[::-1]
    axs[1,1].barh([LABELS.get(x,x) for x in show.index],show.values*100,color=COLORS[3])
    axs[1,1].set(xlabel='Faltantes (%)',title='Calidad antes de imputar')
    fig.tight_layout();savefig('eda.png')

def cluster_analysis(train,test,yt,wt):
    feats=['log_ingreso_pc','log_gasto_pc','altitud','ratio_alumnos_docente','prop_publicas','internet_hogar','electricidad']
    pipe=Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())])
    z=pipe.fit_transform(train[feats]);zt=pipe.transform(test[feats])
    records=[];fitted={}
    for method in ['KMeans','GMM']:
        for k in range(2,7):
            print('Clustering',method,k,flush=True)
            model=(KMeans(n_clusters=k,n_init=10,random_state=SEED) if method=='KMeans' else
                   GaussianMixture(n_components=k,n_init=3,reg_covar=1e-4,random_state=SEED))
            lab=model.fit_predict(z);sizes=np.bincount(lab,minlength=k)
            records.append({'metodo':method,'k':k,'silueta':silhouette_score(z,lab,sample_size=min(2500,len(z)),random_state=SEED),
              'davies_bouldin':davies_bouldin_score(z,lab),'calinski_harabasz':calinski_harabasz_score(z,lab),
              'min_proporcion':sizes.min()/len(z),'elegible':bool(sizes.min()/len(z)>=.05)})
            fitted[(method,k)]=(model,lab)
    result=pd.DataFrame(records);result.to_csv(TAB/'clustering_comparison.csv',index=False)
    eligible=result[result.elegible];eligible=eligible if len(eligible) else result
    chosen=eligible.sort_values(['silueta','davies_bouldin'],ascending=[False,True]).iloc[0]
    key=(chosen.metodo,int(chosen.k));model,lab=fitted[key];labels_test=model.predict(zt)
    profiles=[]
    for i in range(int(chosen.k)):
        m=lab==i;sub=train.iloc[np.flatnonzero(m)];w=wt[m]
        row={'cluster':i,'n':int(m.sum()),'proporcion':m.mean(),'no_uso_ponderado':wm(yt[m],w)}
        for f in ['edad','rural','internet_hogar','electricidad','ingreso_pc_mensual','gasto_pc_mensual','altitud','ratio_alumnos_docente','prop_publicas']+[c for c in train if c.startswith('padlocal_') and pd.api.types.is_numeric_dtype(train[c])]:
            row[f]=wm(sub[f],w)
        row['prop_pobreza']=wm(sub.pobreza.isin([1,2]).astype(float),w)
        row['prop_castellano']=wm(sub.lengua_materna.eq(4).where(sub.lengua_materna.notna()).astype(float),w)
        row['perfil']=('Mayor' if row['internet_hogar']>=.65 else 'Menor')+' conectividad; '+('rural' if row['rural']>=.5 else 'urbano')
        profiles.append(row)
    pd.DataFrame(profiles).to_csv(TAB/'cluster_profiles.csv',index=False)
    pc=PCA(n_components=2,random_state=SEED);proj=pc.fit_transform(z)
    fig,axs=plt.subplots(1,2,figsize=(10,3.7))
    for j,method in enumerate(['KMeans','GMM']):
        r=result[result.metodo.eq(method)];axs[0].plot(r.k,r.silueta,'o-',label=method,color=COLORS[j])
    axs[0].set(xlabel='Número de grupos',ylabel='Silueta (muestra de desarrollo)',title='Comparación de agrupamientos');axs[0].legend()
    rng=np.random.default_rng(SEED);idx=rng.choice(len(z),min(5000,len(z)),replace=False)
    axs[1].scatter(proj[idx,0],proj[idx,1],c=lab[idx],cmap='viridis',s=5,alpha=.45,rasterized=True)
    axs[1].set(xlabel=f'PC1 ({pc.explained_variance_ratio_[0]:.0%})',ylabel=f'PC2 ({pc.explained_variance_ratio_[1]:.0%})',title=f'{key[0]}, k={key[1]}')
    fig.tight_layout();savefig('clustering.png')
    idx=rng.choice(len(z),min(1800,len(z)),replace=False);v=silhouette_samples(z[idx],lab[idx]);y0=10
    plt.figure(figsize=(6,4))
    for i in range(key[1]):
        vals=np.sort(v[lab[idx]==i]);y1=y0+len(vals)
        plt.fill_betweenx(np.arange(y0,y1),0,vals,alpha=.75,color=cm.viridis(i/max(1,key[1]-1)))
        plt.text(-.09,(y0+y1)/2,str(i));y0=y1+10
    plt.axvline(np.mean(v),color='#333333',linestyle='--');plt.xlabel('Coeficiente de silueta');plt.ylabel('Grupo');plt.yticks([])
    plt.title('Silueta del método seleccionado (submuestra)');savefig('silhouette.png')
    joblib.dump({'preprocess':pipe,'model':model,'pca':pc,'features':feats},ROOT/'models/clustering.joblib')
    assignments=pd.concat([pd.DataFrame({'indice':train.index,'particion':'desarrollo','cluster':lab}),
                           pd.DataFrame({'indice':test.index,'particion':'prueba','cluster':labels_test})])
    assignments.to_csv(TAB/'cluster_assignments.csv',index=False)
    stability=[]
    for seed in [42,43,44]:
        for sample_type in ['semilla','submuestra80']:
            idx=np.arange(len(z)) if sample_type=='semilla' else np.random.default_rng(seed).choice(len(z),int(.8*len(z)),replace=False)
            rep=clone(model).set_params(random_state=seed);rep.fit(z[idx]);alt=rep.predict(z)
            stability.append({'seed':seed,'tipo':sample_type,'ari_vs_seleccion':adjusted_rand_score(lab,alt)})
    pd.DataFrame(stability).to_csv(TAB/'clustering_stability.csv',index=False)
    reduced=[f for f in feats if f not in ['electricidad','internet_hogar']]
    zr=clone(pipe).fit_transform(train[reduced]);mr=clone(model);lr=mr.fit_predict(zr)
    ablation={'features':reduced,'silueta':silhouette_score(zr,lr,sample_size=min(2500,len(zr)),random_state=SEED),
      'ari_vs_completo':adjusted_rand_score(lab,lr),'note':'Mismo metodo y k sin electricidad/internet; diagnostico de dependencia de acceso, no nueva seleccion por etiqueta.'}
    dump(TAB/'clustering_access_ablation.json',ablation)
    return {'stability':stability,'access_ablation':ablation,'silhouette_sample_size':min(2500,len(z)),
      'selected':chosen.to_dict(),'profiles':profiles,'pca_variance':pc.explained_variance_ratio_.tolist(),
      'selection_rule':'Máxima silueta entre soluciones con grupos de al menos 5%; DB para desempate. Ajuste sólo en desarrollo.'}

def models_config():
    """24 candidatos HP x5folds +16 estrategias peso x5folds =200 ajustes max."""
    return [
    ('Logística',LogisticRegression(max_iter=2000,random_state=SEED),[{'C':c} for c in [.01,.03,.1,.3,1.,3.]]),
    ('Random Forest',RandomForestClassifier(n_estimators=180,n_jobs=4,random_state=SEED),
      [{'max_depth':d,'min_samples_leaf':l,'max_features':f} for d,l,f in [(8,10,'sqrt'),(None,6,'sqrt'),(12,4,.7),(8,6,.7),(None,12,.7),(16,3,'sqrt')]]),
    ('XGBoost',XGBClassifier(n_estimators=260,learning_rate=.05,subsample=.85,colsample_bytree=.85,
      reg_lambda=5,tree_method='hist',n_jobs=4,random_state=SEED,eval_metric='logloss'),
      [{'max_depth':d,'min_child_weight':c,'reg_lambda':r} for d,c,r in [(2,1,5),(3,1,5),(5,1,5),(3,5,10),(4,5,10),(2,5,1)]]),
    ('CatBoost',CatBoostClassifier(iterations=300,learning_rate=.05,l2_leaf_reg=6,thread_count=4,
      random_seed=SEED,verbose=False,allow_writing_files=False),
      [{'depth':d,'l2_leaf_reg':r} for d,r in [(3,3),(4,6),(6,6),(4,12),(5,3),(6,12)]])]

def preprocess(numeric,categorical):
    return ColumnTransformer([
      ('num',Pipeline([('imputer',SimpleImputer(strategy='median')),('scaler',StandardScaler())]),numeric),
      ('cat',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),
                       ('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),categorical)],
      verbose_feature_names_out=True)

def evaluate_models(train,test,features,cats,y,yt,w,wt):
    numeric=[f for f in features if f not in cats];splits=list(GroupKFold(n_splits=5).split(train,y,groups=train.conglome))
    assert all(set(train.conglome.iloc[a]).isdisjoint(set(train.conglome.iloc[b])) for a,b in splits)
    rows=[];foldrows=[];best_per_model={};oof_per_model={};strategies={};sensitivity=[]
    fold_assignment=np.zeros(len(train),dtype=int)
    for f,(_,b) in enumerate(splits):fold_assignment[b]=f+1
    pd.DataFrame({'indice':train.index,'fold':fold_assignment}).to_csv(TAB/'cv_assignments.csv',index=False)
    for name,est,configs in models_config():
        scores={}
        for strategy in ['uniform','population','class','population_class']:
            oof=np.zeros(len(train));tic=time.perf_counter()
            for a,b in splits:
                pipe=Pipeline([('preprocess',preprocess(numeric,cats)),('model',clone(est).set_params(**configs[0]))])
                pipe.fit(train.iloc[a][features],y[a],model__sample_weight=fitweights(y[a],w[a],strategy))
                oof[b]=pipe.predict_proba(train.iloc[b][features])[:,1]
            vals=[average_precision_score(y[b],oof[b],sample_weight=w[b]) for _,b in splits]
            scores[strategy]=float(np.mean(vals))
            sensitivity.append({'modelo':name,'estrategia':strategy,'ap_cv_media':scores[strategy],
                'ap_oof_no_ponderada':average_precision_score(y,oof),'brier_oof_ponderado':brier_score_loss(y,oof,sample_weight=w),
                'ap_oof_peso_educacion':average_precision_score(y,oof,sample_weight=train.peso_educacion.to_numpy()),'segundos':time.perf_counter()-tic})
        strategies[name]=max(scores,key=scores.get)
        print('Pesos',name,strategies[name],flush=True)
    pd.DataFrame(sensitivity).to_csv(TAB/'weight_sensitivity.csv',index=False)
    for name,est,configs in models_config():
        best=-np.inf
        for j,params in enumerate(configs):
            pred=np.zeros(len(train));foldscores=[];tic=time.perf_counter()
            for fold,(a,b) in enumerate(splits):
                print('CV',name,j+1,'fold',fold+1,flush=True)
                pipe=Pipeline([('preprocess',preprocess(numeric,cats)),('model',clone(est).set_params(**params))])
                pipe.fit(train.iloc[a][features],y[a],model__sample_weight=fitweights(y[a],w[a],strategies[name]))
                pred[b]=pipe.predict_proba(train.iloc[b][features])[:,1]
                m=metrics(y[b],pred[b],w[b]);foldscores.append(m)
                foldrows.append({'modelo':name,'config':j,'fold':fold+1,**m})
            score=np.mean([m['average_precision'] for m in foldscores])
            rows.append({'modelo':name,'config':j,'parametros':json.dumps(params),'ap_cv_media':score,
              'ap_cv_sd':np.std([m['average_precision'] for m in foldscores],ddof=1),
              'auc_cv_media':np.mean([m['roc_auc'] for m in foldscores]),
              'f1_cv_media':np.mean([m['f1_macro'] for m in foldscores]),'estrategia_peso':strategies[name],'segundos':time.perf_counter()-tic})
            if score>best:
                best=score;best_per_model[name]=(est,params);oof_per_model[name]=pred.copy()
    pd.DataFrame(rows).to_csv(TAB/'model_search.csv',index=False)
    pd.DataFrame(foldrows).to_csv(TAB/'cv_folds.csv',index=False)
    search=pd.DataFrame(rows);bestrows=search.loc[search.groupby('modelo').ap_cv_media.idxmax()].sort_values('ap_cv_media',ascending=False)
    bestrows.to_csv(TAB/'model_comparison_cv.csv',index=False)
    winner=bestrows.iloc[0].modelo
    # Selección ya cerrada. La prueba no interviene en modelo, hiperparámetros ni calibración.
    final_models={};calibrators={};testrows=[];probs={};rawprobs={}
    for name,(est,params) in best_per_model.items():
        pipe=Pipeline([('preprocess',preprocess(numeric,cats)),('model',clone(est).set_params(**params))])
        pipe.fit(train[features],y,model__sample_weight=fitweights(y,w,strategies[name]))
        oof=np.clip(oof_per_model[name],1e-6,1-1e-6)
        cal=LogisticRegression(C=1e6,max_iter=1000,random_state=SEED)
        cal.fit(logit(oof).reshape(-1,1),y,sample_weight=w/w.mean())
        raw=pipe.predict_proba(test[features])[:,1]
        prob=cal.predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
        testrows.append({'modelo':name,'seleccionado_cv':name==winner,**metrics(yt,prob,wt),
          'brier_sin_calibrar':brier_score_loss(yt,raw,sample_weight=wt),
          'f1_macro_no_ponderado':f1_score(yt,prob>=.5,average='macro'),
          'auc_no_ponderado':roc_auc_score(yt,prob),**{f'{k}_no_ponderado':v for k,v in metrics(yt,prob,None).items()}})
        final_models[name]=pipe;calibrators[name]=cal;probs[name]=prob;rawprobs[name]=raw
    pd.DataFrame(testrows).to_csv(TAB/'model_comparison_test.csv',index=False)
    baseline=[]
    for name,constant in [('Mayoritario',0.),('Prevalencia desarrollo',wm(y,w))]:
        baseline.append({'modelo':name,**metrics(yt,np.repeat(constant,len(yt)),wt)})
    pd.DataFrame(baseline).to_csv(TAB/'constant_baselines_test.csv',index=False)
    joblib.dump({'pipelines':final_models,'calibrators':calibrators,'strategies':strategies},ROOT/'models/all_models.joblib')
    pd.DataFrame({'indice':train.index,'y':y,'peso':w,**oof_per_model}).to_csv(TAB/'oof_predictions.csv',index=False)
    pred=pd.DataFrame({'indice':test.index,'conglome':test.conglome.values,'y':yt,'peso':wt})
    for name,p in probs.items():pred[name]=p
    pred.to_csv(TAB/'test_predictions.csv',index=False)
    # Curvas de todos los modelos: evaluación comparativa posterior a la selección.
    fig,axs=plt.subplots(1,3,figsize=(12,3.6))
    for i,(name,p) in enumerate(probs.items()):
        fpr,tpr,_=roc_curve(yt,p,sample_weight=wt);pr,re,_=precision_recall_curve(yt,p,sample_weight=wt)
        axs[0].plot(fpr,tpr,color=COLORS[i],label=name)
        axs[1].plot(re,pr,color=COLORS[i])
        bins=pd.cut(p,np.linspace(0,1,11),include_lowest=True)
        xx=[];yy=[]
        for b in bins.categories:
            m=bins==b
            if m.sum()>=10:xx.append(wm(p[m],wt[m]));yy.append(wm(yt[m],wt[m]))
        axs[2].plot(xx,yy,'o-',markersize=3,color=COLORS[i])
    axs[0].plot([0,1],[0,1],'--',color='gray');axs[0].set(xlabel='Falsos positivos',ylabel='Verdaderos positivos',title='ROC ponderada')
    axs[0].legend(fontsize=7,loc='lower right');axs[1].axhline(wm(yt,wt),ls='--',color='gray')
    axs[1].set(xlabel='Recall',ylabel='Precisión',title='Precisión-recall ponderada')
    axs[2].plot([0,1],[0,1],'--',color='gray');axs[2].set(xlabel='Probabilidad media',ylabel='Frecuencia observada',title='Calibración (prueba)')
    fig.tight_layout();savefig('model_curves.png')
    p=probs[winner];cf=confusion_matrix(yt,p>=.5);cw=confusion_matrix(yt,p>=.5,sample_weight=wt)
    plt.figure(figsize=(4.5,3.5));plt.imshow(cf,cmap='Blues')
    for a in range(2):
        for b in range(2):plt.text(b,a,f'{cf[a,b]:,}',ha='center',va='center',color='white' if cf[a,b]>cf.max()/2 else '#172c40',fontsize=16)
    plt.xticks([0,1],CLASS_NAMES);plt.yticks([0,1],CLASS_NAMES)
    plt.xlabel('Predicción');plt.ylabel('Observación');plt.title(f'{winner}: conteos en prueba');savefig('confusion_matrix.png')
    sub=[]
    for var in ['rural','sexo','lengua_materna','pobreza']:
        for val in sorted(test[var].dropna().unique()):
            m=test[var].eq(val).to_numpy()
            if m.sum()>=30 and len(np.unique(yt[m]))==2:
                sub.append({'variable':var,'grupo':val,'n':int(m.sum()),**metrics(yt[m],p[m],wt[m])})
    pd.DataFrame(sub).to_csv(TAB/'subgroup_performance_test.csv',index=False)
    intervals={};rng=np.random.default_rng(SEED);groups=test.conglome.to_numpy();ug=np.unique(groups);stats=[]
    for _ in range(300):
        sampled=rng.choice(ug,len(ug),replace=True);unique,cnt=np.unique(sampled,return_counts=True)
        counts=dict(zip(unique,cnt));mult=np.array([counts.get(g,0) for g in groups]);m=mult>0
        if len(np.unique(yt[m]))==2:
            met=metrics(yt[m],p[m],wt[m]*mult[m]);stats.append([met[k] for k in ['roc_auc','average_precision','f1_macro']])
    for j,k in enumerate(['roc_auc','average_precision','f1_macro']):intervals[k]=np.quantile(np.array(stats)[:,j],[.025,.975]).tolist()
    bundle={'pipeline':final_models[winner],'calibrator':calibrators[winner],'features':features,'threshold':.5,
      'winner':winner,'target':'target_internet','numeric':numeric,'categorical':cats}
    joblib.dump(bundle,ROOT/'models/best_model.joblib')
    dump(ROOT/'models/model_metadata.json',{'winner':winner,'features':features,'threshold':.5,'params':best_per_model[winner][1]})
    return bundle,{'winner':winner,'cv':bestrows.to_dict('records'),'test':testrows,'confusion_counts':cf,
        'confusion_weighted':cw,'bootstrap_95':intervals,'group_bootstraps':len(stats),
        'weight_strategies':strategies,'constant_baselines':baseline,'fits_budget':200,
        'weight_sensitivity':sensitivity,'calibration':'Sigmoide sobre logit de predicciones OOF de desarrollo, con pesos poblacionales. Umbral fijo 0.5.'},p

def explanations(bundle,train,test,y,probs):
    pipe=bundle['pipeline'];ct=pipe.named_steps['preprocess'];model=pipe.named_steps['model'];features=bundle['features']
    rng=np.random.default_rng(SEED);sample=rng.choice(len(test),min(600,len(test)),replace=False)
    correctpos=np.flatnonzero((y==1)&(probs>=.5));correctneg=np.flatnonzero((y==0)&(probs<.5))
    assert len(correctpos) and len(correctneg),'No existen ambos tipos de caso correctamente clasificado.'
    high=correctpos[np.argmax(probs[correctpos])];low=correctneg[np.argmin(probs[correctneg])]
    ids=np.unique(np.r_[sample,high,low]);sub=test.iloc[ids];z=ct.transform(sub[features])
    if isinstance(model,CatBoostClassifier):
        raw=model.get_feature_importance(Pool(z),type='ShapValues');sv=raw[:,:-1];base=raw[:,-1];units='log-odds'
        expected=model.predict(z,prediction_type='RawFormulaVal')
    elif isinstance(model,LogisticRegression):
        background=ct.transform(train[features]);mean=np.mean(background,axis=0)
        sv=(z-mean)*model.coef_[0];base=np.repeat(model.intercept_[0]+mean@model.coef_[0],len(z));units='log-odds'
        expected=model.decision_function(z)
    else:
        explainer=shap.TreeExplainer(model);e=explainer(z)
        sv=e.values;base=e.base_values
        if sv.ndim==3:sv=sv[:,:,1];base=base[:,1]
        if np.ndim(base)==0:base=np.repeat(base,len(z))
        if isinstance(model,RandomForestClassifier):units='probabilidad sin calibrar';expected=model.predict_proba(z)[:,1]
        else:units='log-odds';expected=model.predict(z,output_margin=True)
    residual=float(np.max(np.abs(np.asarray(base)+sv.sum(axis=1)-expected)))
    assert residual<.01,f'SHAP no aditivo: {residual}'
    # Agrupar dummies de cada variable: contribuciones aditivas interpretables.
    names=ct.get_feature_names_out();origin=[]
    for n in names:
        body=n.split('__',1)[1]
        matches=[f for f in features if body==f or body.startswith(f+'_')]
        origin.append(max(matches,key=len))
    aggregated=np.column_stack([sv[:,np.array(origin)==f].sum(axis=1) for f in features])
    data=sub[features].to_numpy(dtype=float);titles=[LABELS.get(f,f) for f in features]
    exp=shap.Explanation(values=aggregated,base_values=np.asarray(base),data=data,feature_names=titles)
    plt.figure();shap.plots.beeswarm(exp,max_display=10,group_remaining_features=False,show=False,plot_size=(8,4.6));plt.title('SHAP global: diez variables principales');savefig('shap_beeswarm.png')
    for j,(f,interaction) in enumerate([('log_gasto_pc','rural'),('internet_hogar','lengua_materna')]):
        plt.figure(figsize=(5.6,3.5))
        shap.dependence_plot(features.index(f),aggregated,data,feature_names=titles,
          interaction_index=features.index(interaction),show=False,ax=plt.gca())
        plt.title(f'Dependencia SHAP: {LABELS[f]}',fontsize=11);savefig(f'shap_dependence_{j+1}.png')
    cases=[]
    for label,row in [('alto',high),('bajo',low)]:
        pos=int(np.flatnonzero(ids==row)[0]);plt.figure();shap.plots.waterfall(exp[pos],max_display=10,show=False)
        plt.title(f'Caso de probabilidad {label} de no uso: p={probs[row]:.3f}',fontsize=11);savefig(f'shap_waterfall_{label}.png')
        cases.append({'caso':label,'indice_dataset':int(test.index[row]),'y':int(y[row]),
          'probabilidad_calibrada':float(probs[row]),'score_base':float(base[pos]),
          'score_modelo':float(expected[pos]),'top_contribuciones':
             sorted([{'variable':f,'shap':float(aggregated[pos,j]),'valor':None if not np.isfinite(data[pos,j]) else float(data[pos,j])} for j,f in enumerate(features)],key=lambda v:abs(v['shap']),reverse=True)[:5]})
    importance=pd.DataFrame({'variable':features,'mean_abs_shap':np.mean(np.abs(aggregated),axis=0)}).sort_values('mean_abs_shap',ascending=False)
    importance.to_csv(TAB/'shap_importance.csv',index=False)
    dump(TAB/'shap_cases.json',cases)
    return {'n_explained':len(ids),'units':units,'max_additivity_residual':residual,'cases':cases,
      'importance':importance.to_dict('records'),'note':'SHAP explica el score previo a calibración. No mide efectos causales. Muestra global no ponderada.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target',choices=['internet'],default='internet');ap.add_argument('--phase',choices=['all','prepare','clustering','supervised','shap'],default='all');args=ap.parse_args()
    df=pd.read_csv(ROOT/'data/processed/dataset_enaho_escale_2025.csv',dtype={'ano':str,'conglome':str,'vivienda':str,'hogar':str,'codperso':str,'ubigeo':str})
    df=df.copy()  # Consolidate blocks before adding deterministic derived columns.
    df,comparison=prepare_targets(df)
    # Derivaciones deterministas: los parámetros estadísticos se ajustarán dentro del fold.
    for origin,f in [('ingreso_pc_mensual','log_ingreso_pc'),('gasto_pc_mensual','log_gasto_pc')]:
        x=pd.to_numeric(df[origin],errors='coerce');df[f]=np.log1p(x.where(x>=0))
    eligible=df.target_internet.notna()&pd.to_numeric(df.peso_persona,errors='coerce').gt(0)
    sub=df[eligible].copy();y=sub.target_internet.to_numpy(dtype=int);w=sub.peso_persona.to_numpy(dtype=float)
    features=['edad','sexo','lengua_materna','rural','pobreza','electricidad','internet_hogar','altitud',
      'log_ingreso_pc','log_gasto_pc','ratio_alumnos_docente','prop_publicas','escale_coincide']
    cats=['sexo','lengua_materna','rural','pobreza','electricidad','internet_hogar','escale_coincide']
    for f in features:sub[f]=pd.to_numeric(sub[f],errors='coerce').astype(float)
    assert_features(features)
    sub.to_csv(ROOT/'data/processed/dataset_modelado_internet_2025.csv',index=True,index_label='indice_dataset')
    sub.rename_axis('indice_dataset').reset_index().to_parquet(ROOT/'data/processed/dataset_modelado_2025.parquet',index=False)
    a,b=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(sub,y,groups=sub.conglome))
    train=sub.iloc[a].copy();test=sub.iloc[b].copy();assert set(train.conglome).isdisjoint(set(test.conglome))
    pd.DataFrame({'indice':sub.index,'particion':np.where(np.isin(np.arange(len(sub)),a),'desarrollo','prueba'),
       'conglome':sub.conglome.values}).to_csv(TAB/'partitions.csv',index=False)
    summary={'target':'No uso de internet durante el mes anterior (P314A=2), en residentes de 6–17 años matriculados y asistentes a primaria/secundaria (P306=P307=1; P308A=2/3), excluida declaración CEBA. Indicador operativo de exclusión digital; no mide competencias.',
      'target_comparison':comparison,'features':features,'seed':SEED,'n_eligible':len(sub),
      'n_train':len(a),'n_test':len(b),'groups_train':train.conglome.nunique(),'groups_test':test.conglome.nunique(),
      'group_overlap':0,'prevalence_train':wm(y[a],w[a]),'prevalence_test':wm(y[b],w[b]),
      'prevalence_total':wm(y,w),'excluded_missing_target_or_weight':int((~eligible).sum()),
      'anti_leak_excluded':['p314a','p314b*','p314d','p315*','p316*','no_uso_internet','exclusion_digital',
       'p306','p307','matriculado','asiste','p308*','p301*','identificadores','coordenadas','mes'],
      'weight':'FACPOB07: factor anual de población del módulo200. Entrenamiento compara uniforme/población/clase/combinado solo en desarrollo.',
      'test_selection':'Una partición GroupShuffleSplit 80/20, semilla42; 5fold GroupKFold en desarrollo.',
      'threshold':.5,'software':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__}}
    from importlib.metadata import version
    summary['software'].update({name:version(name) for name in ['scikit-learn','xgboost','catboost','shap','scipy','matplotlib','joblib']})
    datahash=hashlib.sha256((ROOT/'data/processed/dataset_enaho_escale_2025.csv').read_bytes()).hexdigest()
    codehash=hashlib.sha256(Path(__file__).read_bytes()+(ROOT/'src/nonlinear_shap.py').read_bytes()).hexdigest()
    signature=hashlib.sha256((datahash+codehash).encode()).hexdigest()
    existing=json.loads((ROOT/'reports/results.json').read_text()) if (ROOT/'reports/results.json').exists() else {}
    if existing.get('run_signature')==signature:
        for key in ['clustering','supervised','shap','nonlinear_shap','phase_seconds','measurement_checks']:
            if key in existing:summary[key]=existing[key]
    summary.update({'run_signature':signature,'dataset_sha256':datahash,'analysis_code_sha256':codehash,
      'executed_at_utc':datetime.now(timezone.utc).isoformat(),
      'evaluation_note':'Evaluación retrospectiva sobre una partición de prueba previamente examinada; los resultados requieren validación externa independiente.'})
    summary.setdefault('phase_seconds',{})
    print('Cohorte y particiones',summary['n_train'],summary['n_test'],flush=True)
    with threadpool_limits(limits=4):
        for phase in (['prepare','clustering','supervised','shap'] if args.phase=='all' else [args.phase]):
            tic=time.perf_counter()
            if phase=='prepare':
                from audit_target_measurement import audit_measurement
                measurement=audit_measurement();summary['measurement_checks']=measurement['checks']
                eda(train,features,y[a],w[a])
            if phase=='clustering':summary['clustering']=cluster_analysis(train,test,y[a],w[a])
            if phase=='supervised':
                _,summary['supervised'],_=evaluate_models(train,test,features,cats,y[a],y[b],w[a],w[b])
            if phase=='shap':
                if 'supervised' not in summary:raise RuntimeError('Ejecute primero fase supervised con el mismo código/dataset.')
                bundle=joblib.load(ROOT/'models/best_model.joblib')
                raw=bundle['pipeline'].predict_proba(test[features])[:,1]
                prob=bundle['calibrator'].predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
                summary['shap']=explanations(bundle,train,test,y[b],prob)
                from nonlinear_shap import nonlinear_explanations
                summary['nonlinear_shap']=nonlinear_explanations(train,test,features,summary['supervised'])
            summary['phase_seconds'][phase]=time.perf_counter()-tic
            dump(ROOT/'reports/results.json',summary)
    print('Completado',args.phase,summary.get('supervised',{}).get('winner',''),flush=True)

def assert_features(features):
    prohibited=['p314','p315','p316','target','no_uso','exclusion','p306','p307','p308','p301']
    ids={'conglome','vivienda','hogar','codperso','ubigeo','mes','latitud','longitud','peso_persona','peso_hogar','peso_educacion'}
    bad=[f for f in features if f in ids or any(f.startswith(x) for x in prohibited)]
    if bad:raise ValueError(f'Variables prohibidas por fuga o identificación: {bad}')

if __name__=='__main__':main()
