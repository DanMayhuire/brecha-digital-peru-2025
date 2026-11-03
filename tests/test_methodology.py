"""Pruebas negativas y de aislamiento; no necesitan microdatos."""
import sys, unittest, tempfile
from unittest.mock import patch
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from run_analysis import assert_features,preprocess,fitweights,prepare_targets
from build_data import merge_audit,clean_keys,assert_unique

class MethodologyTests(unittest.TestCase):
    def test_leakage_rejected(self):
        for bad in ['p314a','p314b1_1','p316_5','target_internet','peso_persona','conglome']:
            with self.assertRaises(ValueError):assert_features(['edad',bad])

    def test_preprocessing_training_only(self):
        train=pd.DataFrame({'x':[1.,3.,np.nan],'cat':[1.,2.,1.]})
        test=pd.DataFrame({'x':[1000.,np.nan],'cat':[99.,1.]})
        ct=preprocess(['x'],['cat']);ct.fit(train);before=ct.named_transformers_['num']['imputer'].statistics_.copy()
        z=ct.transform(test)
        np.testing.assert_equal(before,[2.]);np.testing.assert_equal(ct.named_transformers_['num']['imputer'].statistics_,before)
        self.assertTrue(np.isfinite(z).all());self.assertEqual(z.shape[1],3)

    def test_many_to_many_rejected(self):
        with self.assertRaises(pd.errors.MergeError):
            merge_audit(pd.DataFrame({'k':[1,2]}),pd.DataFrame({'k':[1,1]}),['k'],'bad',{'merges':{}})

    def test_keys_padding_and_invalid(self):
        df=clean_keys(pd.DataFrame({'conglome':[' 12 '],'vivienda':['1'],'hogar':['1'],'codperso':['1'],'ubigeo':['10101']}))
        self.assertEqual(df.ubigeo.iloc[0],'010101');self.assertEqual(df.conglome.iloc[0],'000012')
        with self.assertRaises(ValueError):clean_keys(pd.DataFrame({'ubigeo':['1A']}))
        with self.assertRaises(ValueError):assert_unique(pd.DataFrame({'k':[1,1]}),['k'],'duplicate')

    def test_weight_unit_and_class_mass(self):
        y=np.array([0,0,1]);w=np.array([1.,3.,2.])
        combined=fitweights(y,w,'population_class')
        self.assertAlmostEqual(combined[y==0].sum(),combined[y==1].sum())
        np.testing.assert_allclose(fitweights(y,w,'uniform'),np.ones(3))
        self.assertAlmostEqual(fitweights(y,w,'population').mean(),1.)

    def test_missing_target_not_negative(self):
        df=pd.DataFrame({'edad':[10]*4,'p308a':[2]*4,'p308b':[0]*4,'p308c':[5]*4,
            'p306':[1]*4,'p307':[1]*4,'p307d':[np.nan]*4,'p314a':[1,2,np.nan,9],
            'peso_persona':[1]*4,'conglome':['1','2','3','4'],'mes':[3]*4})
        with tempfile.TemporaryDirectory() as tmp,patch('run_analysis.TAB',Path(tmp)):
            out,_=prepare_targets(df)
        np.testing.assert_equal(out.target_internet.to_numpy(),[0,1,np.nan,np.nan])

if __name__=='__main__':unittest.main()
