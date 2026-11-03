"""Recover instructor originals from local outer ZIPs; never invent download URLs."""
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,io,json,os,shutil,zlib,urllib.request
ROOT=Path(__file__).resolve().parents[1]
DRIVE='https://drive.google.com/drive/folders/1J2ExK_k8T9TAveZForau6i90lb8Ef7P2?usp=sharing'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def crc(p):
 value=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):value=zlib.crc32(b,value)
 return value & 0xffffffff
def extract(z,info,dest,reuse):
 dest.parent.mkdir(parents=True,exist_ok=True)
 method='extracted'
 if dest.exists():
  if dest.stat().st_size!=info.file_size or crc(dest)!=info.CRC:raise ValueError('Existing raw file differs; refusing overwrite: '+str(dest))
  method='existing_verified'
 else:
  candidate=reuse/info.filename.split('/')[-1] if reuse else None
  if candidate and candidate.is_file() and candidate.stat().st_size==info.file_size and crc(candidate)==info.CRC:
   os.link(candidate,dest);method='hardlink_existing_identical'
  else:
   tmp=dest.with_suffix(dest.suffix+'.part')
   with z.open(info) as src,tmp.open('wb') as out:shutil.copyfileobj(src,out,4*1024*1024)
   if tmp.stat().st_size!=info.file_size or crc(tmp)!=info.CRC:raise ValueError('Corrupt extraction')
   tmp.replace(dest)
 return {'path':str(dest.relative_to(ROOT/'data/raw')),'bytes':dest.stat().st_size,'sha256':digest(dest),'zip_member':info.filename,'crc32':info.CRC,'materialization':method}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-dir',type=Path,default=None);ap.add_argument('--inei-url');ap.add_argument('--minedu-url');ap.add_argument('--reuse-dir',type=Path,default=None);args=ap.parse_args()
 source=args.source_dir or ROOT/'data/raw/archives';source.mkdir(parents=True,exist_ok=True)
 for prefix,url in [('INEI',args.inei_url),('MINEDU',args.minedu_url)]:
  if url and not list(source.glob(prefix+'*.zip')):
   if not url.startswith('https://'):raise ValueError('HTTPS required')
   dest=source/(prefix+'-teacher.zip');part=dest.with_suffix('.part')
   urllib.request.urlretrieve(url,part)
   if not __import__('zipfile').is_zipfile(part):part.unlink();raise ValueError('URL returned HTML/login instead of ZIP; download manually from instructor Drive')
   part.replace(dest)
 paths={prefix:next(iter(source.glob(prefix+'*.zip')),None) for prefix in ['INEI','MINEDU']}
 if not all(paths.values()):raise SystemExit('Download both instructor ZIPs manually from '+DRIVE+' and pass --source-dir. Direct authenticated URLs may be passed explicitly; none are guessed.')
 raw=ROOT/'data/raw';records=[];archives=[]
 for prefix,p in paths.items():
  archives.append({'path':p.name,'bytes':p.stat().st_size,'sha256':digest(p),'role':'instructor_original'})
  with ZipFile(p) as outer:
   selections=[('vivienda','1474'),('personas','1479'),('educacion','1475'),('sumaria','1478')] if prefix=='INEI' else [('padron','00_Padron'),('padlocal','00_Padlocal')]
   for label,code in selections:
    member=next(n for n in outer.namelist() if (('Modulo'+code+'.zip') if prefix=='INEI' else code+'.zip') in n)
    with ZipFile(io.BytesIO(outer.read(member))) as nested:
     matches=[i for i in nested.infolist() if i.filename.lower().endswith('.csv' if prefix=='INEI' else '.dbf') and '12g' not in i.filename.lower()]
     if len(matches)!=1:raise ValueError('Ambiguous original member '+member)
     info=matches[0];dest=raw/('inei_enaho' if prefix=='INEI' else 'minedu_escale')/Path(info.filename).name
     record=extract(nested,info,dest,args.reuse_dir/('enaho' if prefix=='INEI' else 'escale') if args.reuse_dir else None)
     record.update(module=label,outer_member=member,source_archive=prefix);records.append(record)
 (raw/'teacher_source_manifest.json').write_text(json.dumps({'reference_source':'instructor_panel_2021_2025_cut2025','drive':DRIVE,'archives':archives,'files':records,'note':'Original multiyear CSVs; not annual files. Hardlinks are read-only by policy: never edit raw in place.'},indent=2)+'\n')
 print(json.dumps({'recovered_files':len(records),'files':records},indent=2))
if __name__=='__main__':main()
