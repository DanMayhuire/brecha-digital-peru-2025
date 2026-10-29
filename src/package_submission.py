"""Entrega privada docente; excluye fuentes, entornos, cachés y predicciones por fila."""
from pathlib import Path
import hashlib,json,io,re
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/Entrega_U2_Brecha_Digital_2025.zip'
DIRS=['src','tests','docs','reports','data/raw','data/processed','models','notebooks','output/pdf']
FILES=['README.md','PROJECT_STATUS.md','requirements.txt']
EXCLUDE={'test_predictions.csv','oof_predictions.csv','partitions.csv','cv_assignments.csv','cluster_assignments.csv','01_Revision_de_resultados.ipynb','notebook_execution_attempt1.json','package_verification.json'}
TEXT_EXT={'.md','.json','.py','.txt','.ipynb','.log'}

def portable(data,path):
    if path.suffix not in TEXT_EXT:return data
    text=data.decode('utf-8')
    substitutions=[(str(ROOT),'${PROJECT_ROOT}'),(str(Path.home()/'Downloads/DocenteMaterial'),'${SOURCE_DIR}'),(str(Path.home()/'Downloads'),'${ANNUAL_DIR}'),(str(Path.home()),'${HOME}')]
    for a,b in substitutions:text=text.replace(a,b)
    if path.suffix=='.json':
        def scrub(value):
            if isinstance(value,dict):return {k:scrub(v) for k,v in value.items() if k!='indice_dataset'}
            if isinstance(value,list):return [scrub(v) for v in value]
            return value
        text=json.dumps(scrub(json.loads(text)),ensure_ascii=False,indent=2)+'\n'
    return text.encode('utf-8')

def main():
    verified=json.loads((ROOT/'reports/final_verification.json').read_text())
    if verified['status']!='passed' or not verified['pdf_checked']:raise RuntimeError('Verificación final incompleta; no empaquetar como entrega final.')
    paths=[ROOT/p for p in FILES]
    for name in DIRS:
        paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.ipynb_checkpoints' not in p.parts and p.suffix!='.pyc' and p.name!='.DS_Store' and p.name not in EXCLUDE)
    manifest_path=ROOT/'reports/delivery_manifest.json';paths=sorted(set(p for p in paths if p!=manifest_path))
    payload={str(p.relative_to(ROOT)):portable(p.read_bytes(),p) for p in paths}
    # No logs of row-level examples or filesystem traces are needed to teach/reproduce.
    payload={k:v for k,v in payload.items() if not k.endswith('.log')}
    nbkey='reports/notebook_execution.json'
    if nbkey in payload:
        records=json.loads(payload[nbkey])
        for record in records:
            record['canonical_sha256_before_path_redaction']=record['sha256']
            record['sha256']=hashlib.sha256(payload[record['notebook']]).hexdigest()
        payload[nbkey]=(json.dumps(records,ensure_ascii=False,indent=2)+'\n').encode()
    for key in ['reports/final_verification.json','reports/verification.json']:
        if key in payload:
            verification=json.loads(payload[key])
            verification['packaging_note']='Las pruebas se ejecutaron en el proyecto canónico. El paquete elimina rutas personales e índices de casos SHAP; las huellas de serialización siguientes corresponden al paquete. Se conserva la huella canónica para trazabilidad.'
            for artifact in verification['artifacts']:
                if artifact['path'] in payload:
                    artifact['canonical_sha256_before_path_redaction']=artifact['sha256']
                    artifact['sha256']=hashlib.sha256(payload[artifact['path']]).hexdigest()
                    artifact['bytes']=len(payload[artifact['path']])
            payload[key]=(json.dumps(verification,ensure_ascii=False,indent=2)+'\n').encode()
    manifest={'files':[{'path':k,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in payload.items()],
      'original_archives_included':False,'row_predictions_included':False,
      'purpose':'Entrega privada al docente. No publicación de microdatos. Los datasets procesados anonimizados por INEI conservan llaves técnicas necesarias para auditar uniones; no contienen nombres, DNI ni contactos.',
      'reproduction':'Requiere originales locales: README y data/raw/source_manifest.json. Los hashes se conservan; rutas locales se convierten en variables configurables. Ejecute pipeline para regenerar verificaciones/predicciones locales.',
      'excluded':sorted(EXCLUDE),'text_paths_sanitized':True}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    payload['reports/delivery_manifest.json']=manifest_path.read_bytes()
    OUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUT,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
        for path,data in payload.items():z.writestr('Evaluacion_U2_Brecha_Digital/'+path,data)
    with ZipFile(OUT) as z:
        assert z.testzip() is None
        for row in manifest['files']:
            assert hashlib.sha256(z.read('Evaluacion_U2_Brecha_Digital/'+row['path'])).hexdigest()==row['sha256']
        for path,data in payload.items():
            if Path(path).suffix in TEXT_EXT:assert b'${HOME}' not in data,path
        assert not any(Path(k).name in EXCLUDE for k in payload)
    result={'status':'passed','zip':str(OUT),'files':len(payload),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'crc_and_manifest_verified':True,'personal_paths_removed':True,'row_predictions_excluded':True}
    (ROOT/'reports/package_verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
