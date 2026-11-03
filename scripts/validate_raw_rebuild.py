"""Validate teacher rebuild and existing model without altering scientific artifacts."""
from pathlib import Path
import sys,json,hashlib,subprocess
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from run_analysis import prepare_targets,assert_features,preprocess,SEED
from sklearn.model_selection import GroupShuffleSplit

def main():
 keys=['conglome','vivienda','hogar','codperso'];types={k:str for k in keys+['ubigeo','ano']}
 old=pd.read_csv(ROOT/'data/processed/dataset_enaho_escale_2025.csv',dtype=types)
 new=pd.read_csv(ROOT/'reports/rebuild_teacher/data/processed/dataset_enaho_escale_2025.csv',dtype=types)
 checks={};checks['unique_teacher_keys']=not new.duplicated(keys).any();checks['same_population']=len(old)==len(new)
 a=old.set_index(keys).sort_index();b=new.set_index(keys).sort_index();checks['same_person_keys']=a.index.equals(b.index)
 differences={}
 for c in a.columns.intersection(b.columns):
  x=pd.to_numeric(a[c],errors='coerce').to_numpy(dtype=float);y=pd.to_numeric(b[c],errors='coerce').to_numpy(dtype=float)
  differences[c]=int((~np.isclose(x,y,equal_nan=True,rtol=1e-10,atol=1e-8)).sum())
 checks['common_columns_equal']=not any(differences.values())
 checks['zero_padding']=all(new[c].str.fullmatch(r'\d{'+str(w)+'}').all() for c,w in zip(keys+['ubigeo'],[6,3,2,2,6]))
 for name in ['educacion','vivienda','sumaria','escale']:
  m=json.loads((ROOT/'reports/rebuild_teacher/reports/tables/data_audit.json').read_text())['merges'][name]
  checks['merge_'+name]=m['left_rows']==m['output_rows'] and not m['row_multiplication']
 # Pure target construction, redirect its tables away from historical results.
 import run_analysis
 run_analysis.TAB=ROOT/'reports/raw_management'
 extra=sorted(set(new)-set(old))
 new,_=prepare_targets(new);eligible=new[new.target_internet.notna() & new.peso_persona.gt(0)]
 checks['cohort_16544']=len(eligible)==16544;checks['positive_4294']=int(eligible.target_internet.sum())==4294
 _,test=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(eligible,groups=eligible.conglome))
 historical=pd.read_csv(ROOT/'reports/tables/partitions.csv',dtype={'conglome':str})
 checks['same_test_conglomerates']=set(eligible.iloc[test].conglome)==set(historical.loc[historical.particion.eq('prueba'),'conglome'])
 assertions=json.loads((ROOT/'reports/raw_management/protected_artifacts_before.json').read_text())
 checks['scientific_artifacts_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in assertions.items())
 manifest=json.loads((ROOT/'data/raw/source_manifest.json').read_text())
 for r in manifest['files']:
  p=ROOT/'data/raw'/r['path'];checks['hash_'+r['module']]=p.is_file() and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==r['sha256']
 result={'status':'passed' if all(checks.values()) else 'failed','checks':checks,'different_common_columns':{k:v for k,v in differences.items() if v},'additional_teacher_columns':extra,'n_rebuilt':len(new),'n_model':len(eligible),'full_ml_retrained':False,'reason':'Input equivalence verified by composite person keys; historical artifacts preserved.'}
 (ROOT/'reports/raw_management/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
