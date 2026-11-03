"""Prepare portable notebooks/metadata, preserving local execution evidence. Never push."""
from pathlib import Path
import json,tarfile,datetime,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
 paths=list((ROOT/'notebooks').glob('*.ipynb'))+[ROOT/'docs/sources.json']
 backup=ROOT/'snapshots'/('before_portability_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.tar.gz');backup.parent.mkdir(exist_ok=True)
 with tarfile.open(backup,'w:gz') as archive:
  for p in paths:archive.add(p,arcname=str(p.relative_to(ROOT)))
 for p in paths:
  if p.suffix=='.ipynb':
   notebook=json.loads(p.read_text())
   notebook['metadata'].pop('widgets',None)
   for cell in notebook['cells']:
    # Preserve genuine outputs and execution counts for academic presentation.
    cell.get('metadata',{}).pop('execution',None)
   text=json.dumps(notebook,ensure_ascii=False,indent=1)
   for local,portable in [(str(ROOT),'${PROJECT_ROOT}'),(str(Path.home()),'${HOME}')]:text=text.replace(local,portable)
   p.write_text(text+'\n')
  else:
   data=json.loads(p.read_text())
   for source in data.get('sources',[]):
    if 'outer_archive' in source:source['outer_archive']=Path(source['outer_archive']).name
   p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('Portable notebooks and source metadata prepared; original evidence:',backup.relative_to(ROOT))
if __name__=='__main__':main()
