"""Ejecuta cuatro notebooks en kernels nuevos; guarda log y huellas por ejecución."""
from pathlib import Path
import os,sys,time,json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
for key,rel in [('JUPYTER_CONFIG_DIR','tmp/jupyter/config'),('JUPYTER_DATA_DIR','tmp/jupyter/data'),('JUPYTER_RUNTIME_DIR','tmp/jupyter/runtime'),('IPYTHONDIR','tmp/ipython')]:
    os.environ[key]=str(ROOT/rel);(ROOT/rel).mkdir(parents=True,exist_ok=True)
import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

names=['01_Ingenieria_Datos_EDA','02_Clustering_Perfilamiento','03_Modelado_Supervisado','04_Explicabilidad_SHAP']
def main():
    kernel=ROOT/'tmp/kernel';kernel.mkdir(exist_ok=True)
    (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Proyecto IA','language':'python'}))
    KernelSpecManager().install_kernel_spec(str(kernel),kernel_name='ia-project',user=True,replace=True)
    records=[]
    for name in names:
        path=ROOT/'notebooks'/f'{name}.ipynb';n=nbformat.read(path,as_version=4);tic=time.perf_counter()
        record={'notebook':str(path.relative_to(ROOT)),'started_at_utc':datetime.now(timezone.utc).isoformat(),'status':'running'}
        try:
            print('INICIO',name,flush=True)
            NotebookClient(n,timeout=7200,kernel_name='ia-project',resources={'metadata':{'path':str(ROOT)}},allow_errors=False).execute()
            nbformat.write(n,path);record.update(status='passed',executed_code_cells=sum(c.cell_type=='code' for c in n.cells))
        except Exception as e:
            nbformat.write(n,path);record.update(status='failed',error=str(e));raise
        finally:
            record['seconds']=time.perf_counter()-tic;record['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();records.append(record)
            (ROOT/'reports/notebook_execution.json').write_text(json.dumps(records,indent=2))
        print('FIN',name,record['seconds'],flush=True)
if __name__=='__main__':main()
