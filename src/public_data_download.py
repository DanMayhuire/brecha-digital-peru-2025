"""Download public instructor archives with pinned raw hashes; no local data reuse."""
from pathlib import Path
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from urllib.parse import urlparse,urlencode,urljoin
from urllib.request import build_opener,HTTPCookieProcessor,Request
from zipfile import ZipFile,is_zipfile
import hashlib,json,shutil

class DownloadForm(HTMLParser):
    def __init__(self):super().__init__();self.action=None;self.fields={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form' and a.get('id')=='download-form':self.action=a.get('action')
        if tag=='input' and a.get('name'):self.fields[a['name']]=a.get('value','')

def sha256(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def download(url,path):
    """Anonymous session; handle public large-file confirmation, never authentication."""
    opener=build_opener(HTTPCookieProcessor(CookieJar()))
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);part=path.with_suffix('.part')
    current=url
    for _ in range(3):
        with opener.open(Request(current,headers={'User-Agent':'Mozilla/5.0 (compatible; AcademicDataRecovery/1.0)'}),timeout=90) as response:
            initial=response.read(8192)
            if initial.startswith(b'PK'):
                with part.open('wb') as f:f.write(initial);shutil.copyfileobj(response,f,4*1024*1024)
                if not is_zipfile(part):part.unlink();raise ValueError('Downloaded content is not a valid ZIP')
                part.replace(path);return response.url
            page=initial+response.read(2*1024*1024)
        form=DownloadForm();form.feed(page.decode('utf-8',errors='replace'))
        if not form.action:raise RuntimeError('Public download unavailable: HTML/login/quota instead of ZIP. Download manually using the manifest view_url; no credentials are requested.')
        action=urljoin(current,form.action)
        if urlparse(action).hostname not in {'drive.google.com','drive.usercontent.google.com'}:raise ValueError('Unexpected public confirmation host')
        current=action+'?'+urlencode(form.fields)
    raise RuntimeError('Public download confirmation did not yield a ZIP')

def recover_public(root,lock_path=None):
    root=Path(root);raw=root/'data/raw';lock_path=Path(lock_path or raw/'download_manifest.json')
    lock=json.loads(lock_path.read_text());records=[];downloads=[]
    for item in lock['downloads']:
        expected=item['raw'];dest=raw/expected['path'];archive=raw/'archives'/item['archive_name']
        if dest.is_file():
            if dest.stat().st_size!=expected['bytes'] or sha256(dest)!=expected['sha256']:raise ValueError('Existing original differs; refusing overwrite: '+str(dest))
            materialization='existing_sha256_verified';final_url=None
        else:
            print('Downloading',item['archive_name'],flush=True)
            # Archives are independently verified by the pinned uncompressed content.
            # Never use a local project archive or user download cache.
            final_url=download(item['download_url'],archive)
            with ZipFile(archive) as z:
                members=[i for i in z.infolist() if Path(i.filename).name.lower()==Path(expected['path']).name.lower()]
                if len(members)!=1:raise ValueError('ZIP does not contain the expected original: '+item['archive_name'])
                info=members[0]
                if info.file_size!=expected['bytes']:raise ValueError('Unexpected original size')
                dest.parent.mkdir(parents=True,exist_ok=True);part=dest.with_suffix(dest.suffix+'.part')
                with z.open(info) as f,part.open('wb') as out:shutil.copyfileobj(f,out,4*1024*1024)
                if sha256(part)!=expected['sha256']:part.unlink();raise ValueError('SHA256 mismatch; dataset version changed')
                part.replace(dest)
            materialization='fresh_public_download'
        if dest.suffix=='.csv':
            with dest.open(encoding='utf-8-sig') as f:header=f.readline()
            if 'AÑO_25' not in header.upper():raise ValueError('Expected 2025 panel columns missing')
        else:
            with dest.open('rb') as f:header=f.read(32)
            if len(header)!=32:raise ValueError('Truncated DBF')
        records.append({**expected,'module':item['module'],'source_archive':item['archive_name'],'materialization':materialization})
        downloads.append({'module':item['module'],'download_url':item['download_url'],'view_url':item['view_url'],'resolved_host':urlparse(final_url).hostname if final_url else None,'archive_sha256':sha256(archive) if archive.exists() else None})
        print('SHA256 OK:',expected['path'],flush=True)
    manifest={'reference_source':'instructor_panel_2021_2025_cut2025','drive':lock['folder_url'],'archives':[],'files':records,'downloads':downloads,'note':'Raw files pinned by SHA256. Downloaded from public instructor files; not annual data.'}
    for name in ['teacher_source_manifest.json','source_manifest.json']:(raw/name).write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
