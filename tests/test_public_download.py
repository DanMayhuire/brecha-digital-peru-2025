"""No-network regression checks for pinned public source recovery."""
import io,json,tempfile,unittest,sys,hashlib
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from public_data_download import DownloadForm,recover_public
class PublicRecoveryTests(unittest.TestCase):
 def test_public_confirmation_fields(self):
  p=DownloadForm();p.feed('<form id="download-form" action="https://drive.usercontent.google.com/download"><input name="id" value="abc"><input name="confirm" value="t"></form>')
  self.assertEqual(p.fields,{'id':'abc','confirm':'t'});self.assertIn('drive.usercontent.google.com',p.action)
 def test_mismatched_existing_original_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);raw=root/'data/raw';raw.mkdir(parents=True);(raw/'x.csv').write_bytes(b'wrong')
   (raw/'download_manifest.json').write_text(json.dumps({'downloads':[{'module':'x','archive_name':'x.zip','raw':{'path':'x.csv','bytes':5,'sha256':'0'*64}}]}))
   with self.assertRaises(ValueError):recover_public(root)
   self.assertEqual((raw/'x.csv').read_bytes(),b'wrong')
 def test_downloaded_version_hash_is_enforced(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);raw=root/'data/raw';raw.mkdir(parents=True)
   (raw/'download_manifest.json').write_text(json.dumps({'downloads':[{'module':'x','archive_name':'x.zip','download_url':'https://drive.google.com/uc?id=x','raw':{'path':'x.csv','bytes':5,'sha256':'0'*64}}]}))
   def fake_download(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,'w') as z:z.writestr('x.csv',b'wrong')
    return url
   with patch('public_data_download.download',fake_download):
    with self.assertRaises(ValueError):recover_public(root)
   self.assertFalse((raw/'x.csv').exists())
if __name__=='__main__':unittest.main()
