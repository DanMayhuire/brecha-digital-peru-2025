"""Publish genuinely executed phase notebooks and a labelled combined presentation."""
from pathlib import Path
import json,hashlib,copy,base64,io
import nbformat
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'reports/rebuild_teacher'
def main():
 records=json.loads((RUN/'reports/notebook_execution.json').read_text());assert len(records)==4 and all(r['status']=='passed' for r in records)
 combined=nbformat.v4.new_notebook();combined.metadata={'kernelspec':{'name':'ia-u2','display_name':'Python IA U2','language':'python'},'presentation_provenance':'Outputs compiled from four actually executed phase notebooks; separate fresh kernels, original counters retained.'}
 results=json.loads((RUN/'reports/results.json').read_text());best=next(x for x in results['supervised']['test'] if x['seleccionado_cv'])
 combined.cells=[nbformat.v4.new_markdown_cell('# Proyecto completo — resultados ejecutados\n\n**Listo para exposición: abra este archivo y desplácese. No hace falta ejecutar celdas ni descomprimir datos para ver los resultados.**\n\nFuente: originales del profesor, corte2025. Este recorrido reúne los cuatro notebooks ejecutados de verdad en kernels independientes; conserva sus salidas y contadores originales por fase. No es una simulación ni afirma una única ejecución en un solo kernel. Para recalcular, use las fases individuales en orden.\n\nCohorte: '+str(results['n_eligible'])+' estudiantes. Ganador CV: '+results['supervised']['winner']+f". Prueba ponderada: ROC-AUC {best['roc_auc']:.4f}, AP {best['average_precision']:.4f}, F1macro {best['f1_macro']:.4f}.\n\nLa prueba ya fue observada previamente; los resultados no acreditan causalidad ni medición completa de competencias digitales.")]
 evidence=[]
 for record in records:
  path=RUN/record['notebook'];nb=nbformat.read(path,as_version=4)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
  images=0;tables=0;code=0
  for cell in nb.cells:
   if cell.cell_type=='code':
    code+=1;assert cell.execution_count is not None and cell.outputs
    for o in cell.outputs:
     assert o.output_type!='error'
     data=o.get('data',{})
     if 'image/png' in data:
      Image.open(io.BytesIO(base64.b64decode(data['image/png']))).verify();images+=1
     if '<table' in data.get('text/html',''):tables+=1
  assert images>0 and tables>0
  text=nbformat.writes(nb)
  # Redact only installation paths in a saved progress-bar warning; keep all results and warnings.
  text=text.replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${HOME}')
  nb=nbformat.reads(text,as_version=4)
  assert str(Path.home()) not in text and ('/'+'var/folders/') not in text
  (ROOT/record['notebook']).write_text(text)
  combined.cells.append(nbformat.v4.new_markdown_cell('---\n\n## Fase ejecutada: '+path.name+'\n\nInicio UTC: '+record['started_at_utc']+f". Duración observada: {record['seconds']:.1f}s. Código ejecutado en kernel nuevo; salidas conservadas."))
  combined.cells.extend(copy.deepcopy(nb.cells))
  evidence.append({**record,'embedded_images':images,'embedded_tables':tables,'executed_code_cells':code,'presentation_file':record['notebook'],'presentation_sha256':hashlib.sha256((ROOT/record['notebook']).read_bytes()).hexdigest()})
 out=ROOT/'notebooks/00_Proyecto_Completo_Ejecutado.ipynb';nbformat.write(combined,out)
 # Verify persisted JSON, not only objects in memory.
 saved=nbformat.read(out,as_version=4);assert all(c.execution_count is not None for c in saved.cells if c.cell_type=='code')
 report={'status':'passed','phases':evidence,'combined':str(out.relative_to(ROOT)),'combined_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'combined_bytes':out.stat().st_size,'images':sum(x['embedded_images'] for x in evidence),'tables':sum(x['embedded_tables'] for x in evidence),'errors':0,'note':'Historical scientific artifacts remain intact; current teacher results stay under reports/rebuild_teacher.'}
 (ROOT/'reports/raw_management/presentation_execution.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['status','combined','combined_bytes','images','tables','errors']},indent=2))
if __name__=='__main__':main()
