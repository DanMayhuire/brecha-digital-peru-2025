import sys,tempfile,unittest,io,json
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
from download_raw_data import extract
from teacher_inputs import load_teacher
from build_data import clean_keys,assert_unique,HH,PERSON
class RawRecoveryTests(unittest.TestCase):
 def test_original_existing_file_is_never_overwritten(self):
  raw=ROOT/'data/raw'
  with tempfile.TemporaryDirectory(dir=raw) as temp:
   p=Path(temp)/'source.csv';p.write_bytes(b'old original')
   buf=io.BytesIO()
   with ZipFile(buf,'w') as z:z.writestr('source.csv',b'new data')
   with ZipFile(buf) as z:
    with self.assertRaises(ValueError):extract(z,z.getinfo('source.csv'),p,None)
   self.assertEqual(p.read_bytes(),b'old original')
 def test_panel_cut_preserves_text_year_and_zeroes(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'x.csv').write_text('AÑO_25,CONGLOME_25,VIVIENDA_25,HOGAR_25,CODPERSO_25,P208A_25\n2025,000012,001,01,01,12\n2024,000013,001,01,01,14\n',encoding='utf-8-sig')
   (root/'teacher_source_manifest.json').write_text(json.dumps({'files':[{'module':'personas','path':'x.csv'}]}))
   df=load_teacher(root,'personas',{'año',*PERSON,'p208a'},clean_keys,assert_unique,HH,PERSON,{'modules':{}})
   self.assertEqual(len(df),1);self.assertEqual(df.conglome.iloc[0],'000012');self.assertEqual(df['año'].iloc[0],'2025')
if __name__=='__main__':unittest.main()
