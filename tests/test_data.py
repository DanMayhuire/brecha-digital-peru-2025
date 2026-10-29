"""Source parsing regressions and invariants in the rebuilt analytical dataset."""
import json,sys,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build_data import clean_keys,assert_unique,HH,PERSON
from source_audit import load_annual

class SourceParsingTests(unittest.TestCase):
    def test_decimal_comma_keys_and_target_missing_codes(self):
        # Regression: annual decimals cannot be parsed with panel CSV settings.
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'1031-Modulo03.zip'
            with ZipFile(p,'w') as z:
                z.writestr('1031-Modulo03/Enaho01A-2025-300.csv',
                    'AÑO;CONGLOME;VIVIENDA;HOGAR;CODPERSO;P300A;P308B;P314A;FACTORA07\n2025;000012;001;01;01;99;9;2;123,456\n2025;000012;001;01;02;9;3;1;50,5\n'.encode('latin1'))
            df=load_annual(temp,'educacion',{'año',*PERSON,'p300a','p308b','p314a','factora07'},clean_keys,assert_unique,HH,PERSON,{'modules':{}})
            self.assertAlmostEqual(df.factora07.iloc[0],123.456)
            self.assertTrue(pd.isna(df.p300a.iloc[0]));self.assertEqual(df.p300a.iloc[1],9)
            self.assertTrue(pd.isna(df.p308b.iloc[0]));self.assertEqual(df.conglome.iloc[0],'000012')
            self.assertEqual(df['año'].iloc[0],'2025')

    def test_rejects_duplicate_annual_people(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'1031-Modulo02.zip'
            with ZipFile(p,'w') as z:
                z.writestr('Enaho01-2025-200.csv',('AÑO;CONGLOME;VIVIENDA;HOGAR;CODPERSO\n'+'2025;000012;001;01;01\n'*2).encode('latin1'))
            with self.assertRaises(ValueError):
                load_annual(temp,'personas',{'año',*PERSON},clean_keys,assert_unique,HH,PERSON,{'modules':{}})

class RebuiltDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=pd.read_parquet(ROOT/'data/processed/dataset_enaho_escale_2025.parquet')
        cls.audit=json.loads((ROOT/'reports/tables/data_audit.json').read_text())

    def test_person_keys_and_year_preserved(self):
        d=self.data
        self.assertFalse(d.duplicated(['ano',*PERSON]).any())
        for c,w in [('conglome',6),('vivienda',3),('hogar',2),('codperso',2),('ubigeo',6)]:
            self.assertTrue(d[c].str.fullmatch(r'\d{'+str(w)+'}').all(),c)
        self.assertEqual(set(d.ano),{'2025'});self.assertTrue(d.edad.between(6,17).all())
        self.assertNotIn('latitud',d);self.assertNotIn('longitud',d)

    def test_no_multiplication_and_geographic_keys(self):
        for name,m in self.audit['merges'].items():
            self.assertEqual(m['left_rows'],m['output_rows'],name)
            self.assertFalse(m['row_multiplication'],name)
        self.assertEqual(self.audit['person_household_ubigeo_mismatches'],0)
        self.assertTrue(self.data.escale_area.eq(self.data.rural+1).all())

    def test_padlocal_is_unique_and_not_double_counted(self):
        e=self.audit['escale'];dim=pd.read_parquet(ROOT/'data/processed/escale_locales_dimension_2025.parquet')
        self.assertFalse(dim.CODLOCAL.duplicated().any())
        self.assertEqual(e['services_before_local_join'],e['services_after_local_join'])
        self.assertEqual(e['area_conflicting_services'],0)
        agg=pd.read_parquet(ROOT/'data/processed/escale_distrito_area_2025.parquet')
        self.assertTrue((agg.escale_locales<=agg.escale_servicios).all())
        self.assertTrue(agg.escale_cobertura_padlocal.between(0,1).all())
        np.testing.assert_allclose(agg.ratio_alumnos_docente,agg.escale_alumnos/agg.escale_docentes)

    def test_raw_eda_parsing_and_source_choice(self):
        raw=pd.read_csv(ROOT/'reports/tables/raw_eda_variables.csv')
        self.assertEqual(raw.numeric_parse_failures.sum(),0)
        self.assertGreater(raw.decimal_comma_values.sum(),0)
        manifest=json.loads((ROOT/'data/raw/source_manifest.json').read_text())
        self.assertEqual(manifest['reference_source'],'annual_2025')
        for c in ['p314b_1','p316_5','p316b','p316c1','p316c10']:
            self.assertIn(c,self.data)

if __name__=='__main__':unittest.main()
