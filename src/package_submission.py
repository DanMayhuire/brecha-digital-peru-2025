"""Package publication files with a SHA-256 inventory and ZIP integrity checks."""
from pathlib import Path
import hashlib,json,subprocess
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/Entrega_U2_Brecha_Digital_2025.zip'

def publication_paths():
    candidates=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    return sorted({ROOT/p for p in candidates if (ROOT/p).is_file() and p!='reports/delivery_manifest.json' and not p.endswith('.zip')})

def main():
    verification=json.loads((ROOT/'reports/final_verification.json').read_text())
    if verification['status']!='passed':raise ValueError('Complete verification first')
    subprocess.run(['python3',str(ROOT/'scripts/check_github_ready.py')],cwd=ROOT,check=True)
    payload={str(p.relative_to(ROOT)):p.read_bytes() for p in publication_paths()}
    manifest={'files':[{'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for p,b in payload.items()],'original_data_included':False,'individual_evaluation_traces_included':False}
    payload['reports/delivery_manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    OUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUT,'w',compression=ZIP_DEFLATED,compresslevel=6) as archive:
        for path,data in payload.items():archive.writestr('Evaluacion_U2_Brecha_Digital/'+path,data)
    with ZipFile(OUT) as archive:
        assert archive.testzip() is None
        for row in manifest['files']:assert hashlib.sha256(archive.read('Evaluacion_U2_Brecha_Digital/'+row['path'])).hexdigest()==row['sha256']
    print(json.dumps({'zip':str(OUT.relative_to(ROOT)),'files':len(payload),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()
