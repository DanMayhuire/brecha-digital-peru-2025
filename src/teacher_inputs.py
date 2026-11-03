"""Read original instructor files without pretending the panel is annual ENAHO."""
from pathlib import Path
import io,json
from zipfile import ZipFile,ZIP_STORED
import pandas as pd
from source_audit import MISSING_CODES

def load_teacher(raw,name,wanted,clean_keys,assert_unique,hh,person,audit):
 from build_data import canonical,strip_year
 manifest=json.loads((Path(raw)/'teacher_source_manifest.json').read_text());record=next(r for r in manifest['files'] if r['module']==name)
 path=Path(raw)/record['path'];parts=[];scanned=0
 with path.open('rb') as f:
  for chunk in pd.read_csv(f,encoding='utf-8-sig',dtype='string',chunksize=10000,usecols=lambda c:canonical(c).endswith('_25') and strip_year(c) in wanted):
   scanned+=len(chunk);chunk.columns=[strip_year(c) for c in chunk]
   for c in chunk:chunk[c]=chunk[c].str.strip().replace('',pd.NA)
   mask=chunk['año'].eq('2025') & chunk.conglome.notna()
   parts.append(chunk.loc[mask].copy())
 frame=clean_keys(pd.concat(parts,ignore_index=True));assert_unique(frame,['año',*(person if name in ['personas','educacion'] else hh)],name)
 for c in frame:
  if c not in {'año','mes','ubigeo','nconglome','sub_conglome',*person}:
   frame[c]=pd.to_numeric(frame[c],errors='coerce')
   if c in MISSING_CODES:frame[c]=frame[c].replace(MISSING_CODES[c],float('nan'))
 # Raw EDA on the 2025 original cut, before joins/imputation. Full multiyear originals remain intact.
 for c in frame:
  num=pd.to_numeric(frame[c],errors='coerce');row={'module':name,'variable':c,'rows':len(frame),'missing_raw':int(frame[c].isna().sum()),'missing_pct':float(frame[c].isna().mean()*100),'numeric_parse_failures':0,'decimal_comma_values':0}
  if c not in {*person,'ubigeo','año','mes'}:
   for q in [0,.01,.25,.5,.75,.99,1]:row[f'q{int(q*100):02}']=float(num.quantile(q)) if num.notna().any() else None
  audit.setdefault('raw_eda',[]).append(row)
 audit['modules'][name]={'source_member':record['path'],'encoding':'utf-8-sig','separator':',','decimal':'.','rows_with_2025_identifiers':len(frame),'all_year_rows_scanned':scanned,'unique_keys':True,'conglomerates':int(frame.conglome.nunique()),'columns':list(frame)}
 return frame

class RawEscale:
 def __init__(self,root):self.root=Path(root)
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def namelist(self):return ['MINEDU/00_Padron.zip','MINEDU/00_Padlocal.zip']
 def read(self,member):
  name='Padlocal.dbf' if 'Padlocal' in member else 'Padron.dbf'
  path=next(p for p in (self.root/'minedu_escale').iterdir() if p.name.lower()==name.lower())
  buffer=io.BytesIO()
  with ZipFile(buffer,'w',compression=ZIP_STORED) as z:z.write(path,arcname=name)
  return buffer.getvalue()
