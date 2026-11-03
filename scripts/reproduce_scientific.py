"""Isolated retraining against the frozen scientific reference, never promotion.

Inputs are the versioned processed data; recovery from the instructor originals
remains a separately labelled experiment because its row order differs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import joblib
from scipy.special import logit
from sklearn.base import clone

ROOT=Path(__file__).resolve().parents[1]


def compare_run(run):
    reference=json.loads((ROOT/'reports/results.json').read_text())
    actual=json.loads((run/'reports/results.json').read_text())
    checks=[]
    def check(name,condition):
        checks.append({'name':name,'passed':bool(condition)})
    for key in ['dataset_sha256','analysis_code_sha256','features','n_eligible','n_train','n_test','group_overlap','threshold']:
        check(key,reference[key]==actual[key])
    check('winner_unchanged',reference['supervised']['winner']==actual['supervised']['winner']=='CatBoost')
    for family in reference['supervised']['test']:
        other=next(x for x in actual['supervised']['test'] if x['modelo']==family['modelo'])
        check('metrics_'+family['modelo'],all(np.isclose(v,other[k],rtol=1e-8,atol=1e-10) for k,v in family.items() if isinstance(v,(float,int)) and not isinstance(v,bool)))
    # Independently compare the regenerated test rows against the original bundles,
    # including on clones where individual reference traces are intentionally absent.
    data=pd.read_csv(ROOT/'data/processed/dataset_modelado_internet_2025.csv').set_index('indice_dataset')
    pred=pd.read_csv(run/'reports/tables/test_predictions.csv');oof=pd.read_csv(run/'reports/tables/oof_predictions.csv')
    bundles=joblib.load(ROOT/'models/all_models.joblib')
    for name,pipe in bundles['pipelines'].items():
        raw=pipe.predict_proba(data.loc[pred.indice,reference['features']])[:,1];cal=bundles['calibrators'][name]
        p=cal.predict_proba(logit(np.clip(raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
        check('frozen_model_prediction_'+name,np.allclose(p,pred[name],rtol=1e-8,atol=1e-10))
        fitted=clone(cal).fit(logit(np.clip(oof[name].to_numpy(),1e-6,1-1e-6)).reshape(-1,1),oof.y,sample_weight=oof.peso/oof.peso.mean())
        check('frozen_oof_calibration_'+name,np.allclose(fitted.coef_,cal.coef_) and np.allclose(fitted.intercept_,cal.intercept_))
    deltas={};unavailable=[]
    for name in ['test_predictions.csv','oof_predictions.csv','cv_assignments.csv','partitions.csv','cluster_assignments.csv','clustering_comparison.csv','cluster_profiles.csv','clustering_stability.csv','model_comparison_cv.csv','cv_folds.csv','shap_importance.csv','shap_interactions_xgboost.csv']:
        if not (ROOT/'reports/tables'/name).exists():
            unavailable.append(name);continue
        a=pd.read_csv(ROOT/'reports/tables'/name);b=pd.read_csv(run/'reports/tables'/name)
        ok=list(a)==list(b) and len(a)==len(b);delta=0.
        if ok:
            for col in a:
                if col in ['segundos']:continue
                if pd.api.types.is_numeric_dtype(a[col]):
                    ok &= bool(np.allclose(a[col],b[col],rtol=1e-8,atol=1e-9,equal_nan=True))
                    d=np.abs(a[col].astype(float)-b[col].astype(float));delta=max(delta,float(d.max()) if d.notna().any() else 0.)
                else:ok &= a[col].fillna('<NA>').equals(b[col].fillna('<NA>'))
        check('table_'+name,ok);deltas[name]=delta
    for k in ['silueta','ari_vs_completo']:
        check('ablation_'+k,np.isclose(reference['clustering']['access_ablation'][k],actual['clustering']['access_ablation'][k]))
    result={'status':'passed' if all(c['passed'] for c in checks) else 'failed','executed_at_utc':datetime.now(timezone.utc).isoformat(),'reference_dataset_sha256':reference['dataset_sha256'],'analysis_code_sha256':reference['analysis_code_sha256'],'checks':checks,'max_absolute_numeric_difference_by_table':deltas,'reference_tables_not_present_locally':unavailable,'metrics':actual['supervised']['test'],'historical_test_warning':reference['historical_test_warning'],'scope':'Full 200-fit training, clustering and SHAP from frozen versioned processed data, in an isolated directory. No automatic promotion of models. Raw-source equivalence is audited separately.'}
    (ROOT/'docs/SCIENTIFIC_REPRODUCTION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if result['status']!='passed':raise ValueError('Isolated reproduction differs; see docs/SCIENTIFIC_REPRODUCTION.json')
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-dir',type=Path,default=ROOT/'tmp/scientific_reproduction');ap.add_argument('--compare-existing',action='store_true',help='Only compare a previously executed isolated run; does not claim to rerun it');ap.add_argument('--restore-evaluation-traces',action='store_true',help='After successful comparison, copy missing ignored evaluation traces back; never overwrite models or existing traces');args=ap.parse_args();run=args.run_dir.resolve()
    if run==ROOT or ROOT in run.parents and run.relative_to(ROOT).parts[0] not in {'tmp','reports'}:raise ValueError('Use an isolated tmp or reports directory')
    if not args.compare_existing:
        if run.exists():raise FileExistsError('Use a new isolated directory to preserve prior runs')
        for folder in ['src','tests','docs','data/processed']:
            shutil.copytree(ROOT/folder,run/folder)
        (run/'reports').mkdir(exist_ok=True)
        env={**os.environ,'MPLCONFIGDIR':str(run/'tmp/matplotlib'),'XDG_CACHE_HOME':str(run/'tmp/cache')}
        with (run/'reports/retraining.log').open('w') as log:
            subprocess.run([sys.executable,'-B',str(run/'src/run_analysis.py')],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    result=compare_run(run)
    if args.restore_evaluation_traces:
        for name in ['test_predictions.csv','oof_predictions.csv','partitions.csv','cv_assignments.csv','cluster_assignments.csv','cv_folds.csv']:
            dest=ROOT/'reports/tables'/name
            if not dest.exists():shutil.copy2(run/'reports/tables'/name,dest)
    print(json.dumps({'status':result['status'],'checks':len(result['checks']),'automatic_promotion':False},indent=2))


if __name__=='__main__':main()
