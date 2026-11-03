"""Interacciones de XGBoost: complemento explícito, sin sustituir ganador CV.

TreeSHAP path-dependent usa cobertura de árboles de desarrollo como referencia.
Las interacciones se calculan en hasta180 casos de prueba elegidos con semilla42.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap,joblib
ROOT=Path(__file__).resolve().parents[1]

def nonlinear_explanations(train,test,features,supervised):
    from run_analysis import dump,savefig,LABELS,SEED,TAB
    allmodels=joblib.load(ROOT/'models/all_models.joblib');pipe=allmodels['pipelines']['XGBoost']
    ct=pipe.named_steps['preprocess'];model=pipe.named_steps['model']
    ids=np.random.default_rng(SEED).choice(len(test),min(180,len(test)),replace=False)
    sub=test.iloc[ids];z=ct.transform(sub[features]);ex=shap.TreeExplainer(model,feature_perturbation='tree_path_dependent',model_output='raw')
    iv=np.asarray(ex.shap_interaction_values(z));sv=np.asarray(ex.shap_values(z))
    expected=model.predict(z,output_margin=True);base=float(np.asarray(ex.expected_value).ravel()[0])
    residual=float(np.max(np.abs(base+iv.sum(axis=(1,2))-expected)))
    rows_residual=float(np.max(np.abs(iv.sum(axis=2)-sv)))
    assert residual<.01 and rows_residual<.01,(residual,rows_residual)
    names=ct.get_feature_names_out();origin=[]
    for n in names:
        body=n.split('__',1)[1];origin.append(max([f for f in features if body==f or body.startswith(f+'_')],key=len))
    indices=[np.flatnonzero(np.array(origin)==f) for f in features]
    aggregated=np.stack([sv[:,idx].sum(axis=1) for idx in indices],axis=1)
    groupiv=np.zeros((len(z),len(features),len(features)))
    for i,idx in enumerate(indices):
        for j,jdx in enumerate(indices):groupiv[:,i,j]=iv[:,idx,:][:,:,jdx].sum(axis=(1,2))
    assert np.allclose(groupiv.sum(axis=(1,2)),iv.sum(axis=(1,2)),atol=1e-5)
    focus={'lengua_materna','rural','internet_hogar','log_gasto_pc','log_ingreso_pc','ratio_alumnos_docente','prop_publicas','pobreza','altitud'}
    pairs=[]
    for i,a in enumerate(features):
        for j,b in enumerate(features):
            if i<j and a in focus and b in focus:
                pairs.append({'variable_1':a,'variable_2':b,'mean_abs_pair_contribution':float(np.mean(np.abs(2*groupiv[:,i,j])))})
    pairs=sorted(pairs,key=lambda p:p['mean_abs_pair_contribution'],reverse=True)
    pd.DataFrame(pairs).to_csv(TAB/'shap_interactions_xgboost.csv',index=False)
    titles=[LABELS.get(f,f) for f in features];data=sub[features].to_numpy(dtype=float)
    for k,pair in enumerate(pairs[:2],1):
        i=features.index(pair['variable_1']);j=features.index(pair['variable_2'])
        fig,ax=plt.subplots(figsize=(5.9,3.8))
        shap.dependence_plot(i,aggregated,data,feature_names=titles,interaction_index=j,show=False,ax=ax)
        ax.set_title(f'XGBoost: dependencia de {titles[i]}',fontsize=10);fig.tight_layout();savefig(f'shap_nonlinear_dependence_{k}.png')
        fig,ax=plt.subplots(figsize=(5.9,3.8))
        sc=ax.scatter(data[:,i],2*groupiv[:,i,j],c=data[:,j],cmap='viridis',s=14,alpha=.65)
        ax.axhline(0,color='gray',lw=.7);ax.set(xlabel=titles[i],ylabel='Contribución de interacción 2φij (log-odds)',title='XGBoost: interacción TreeSHAP')
        fig.colorbar(sc,ax=ax,label=titles[j]);fig.tight_layout();savefig(f'shap_interaction_{k}.png')
    result={'model':'XGBoost','winner':supervised['winner'],'role':'Ganador real' if supervised['winner']=='XGBoost' else 'Análisis complementario; no sustituye al ganador',
      'n_explained':len(z),'sample_seed':SEED,'units':'log-odds antes de calibrar','background':'TreeSHAP tree_path_dependent: cobertura de hojas ajustada en desarrollo',
      'max_additivity_residual':residual,'max_interaction_row_residual':rows_residual,'pairs':pairs[:10],
      'note':'El par aporta 2*phi_ij al score; las interacciones son propiedades predictivas del árbol ajustado, no efectos causales ni pruebas de significación. La selección de pares es exploratoria posterior al ajuste.'}
    dump(TAB/'nonlinear_shap.json',result);return result
