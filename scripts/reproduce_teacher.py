"""Reproduce in an isolated run directory; scientific artifacts are evaluated in a separate directory."""
from pathlib import Path
import argparse,subprocess,sys,shutil,os,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run-dir',type=Path,default=ROOT/'reports/teacher_run');ap.add_argument('--link-raw',action='store_true',help='Optional same-volume hardlinks; default copies raw files');ap.add_argument('--train',action='store_true',help='Also rerun models, SHAP, report and verification; no notebooks');args=ap.parse_args()
 run=args.run_dir.resolve()
 if run==ROOT:raise ValueError('Choose an isolated directory to protect existing results')
 for folder in ['src','tests','docs','scripts']:
  shutil.copytree(ROOT/folder,run/folder,dirs_exist_ok=True)
 for name in ['README.md','requirements.txt']:shutil.copy2(ROOT/name,run/name)
 raw=run/'data/raw';raw.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((ROOT/'data/raw/source_manifest.json').read_text())
 for record in manifest['files']:
  dest=raw/record['path'];dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():
   if args.link_raw:os.link(ROOT/'data/raw'/record['path'],dest)
   else:shutil.copy2(ROOT/'data/raw'/record['path'],dest)
 for name in ['source_manifest.json','teacher_source_manifest.json','README.md']:shutil.copy2(ROOT/'data/raw'/name,raw/name)
 env={**os.environ,'MPLCONFIGDIR':str(ROOT/'tmp/matplotlib'),'XDG_CACHE_HOME':str(ROOT/'tmp/cache')}
 commands=[['src/build_data.py','--source','teacher','--raw-dir',str(raw),'--run-dir',str(run)]]
 if args.train:commands += [['src/run_analysis.py'],['src/audit_target_measurement.py'],['src/update_model_dictionary.py'],['src/make_report.py'],['src/verify_outputs.py','--skip-notebooks']]
 for command in commands:subprocess.run([sys.executable,*command],cwd=run,env=env,check=True)
 print('Reproduction complete:',run,'; training executed:',args.train)
if __name__=='__main__':main()
