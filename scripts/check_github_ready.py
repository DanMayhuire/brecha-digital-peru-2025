"""Read-only checks on files Git would publish, not on private local results."""
from pathlib import Path
import subprocess,json,re,ast
ROOT=Path(__file__).resolve().parents[1]
def main():
 files=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines())
 failures=[]
 individual={'test_predictions.csv','oof_predictions.csv','partitions.csv','cv_assignments.csv','cluster_assignments.csv','shap_cases.json'}
 personal=re.compile('/'+r'Users/[^/\s]+|/'+r'home/[^/\s]+|/'+'(?:private/)?var/folders/')
 for rel in sorted(files):
  p=ROOT/rel
  if not p.is_file():continue
  if rel.startswith(('data/processed/','models/','snapshots/','tmp/','reports/rebuild_teacher/','output/BI_')) or p.name in individual:failures.append([rel,'private artifact selected'])
  if rel.startswith('data/raw/') and p.suffix.lower() in {'.csv','.dbf','.zip'}:failures.append([rel,'original data selected'])
  if p.suffix in {'.py','.md','.json','.ipynb','.txt','.log'}:
   text=p.read_text()
   if personal.search(text):failures.append([rel,'personal absolute path'])
   if re.search(r'(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]{20,}',text):failures.append([rel,'possible secret'])
  if p.suffix=='.ipynb':
   n=json.loads(p.read_text())
   for c in n['cells']:
    if c['cell_type']=='code':
     if c.get('execution_count') is None:failures.append([rel,'cell has not been executed'])
     if any(o.get('output_type')=='error' for o in c.get('outputs',[])):failures.append([rel,'saved execution error'])
     ast.parse(''.join(c['source']))
 print(json.dumps({'status':'passed' if not failures else 'failed','candidate_files':len(files),'failures':failures},indent=2))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
