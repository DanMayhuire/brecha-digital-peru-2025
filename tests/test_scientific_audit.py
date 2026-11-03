"""Regressions for silent changes to evaluation row identity/order."""
import sys
from pathlib import Path
import unittest
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from scientific_audit import aligned_predictions


class PredictionAlignmentTests(unittest.TestCase):
    def test_aligns_by_saved_identity_instead_of_current_row_order(self):
        model=pd.DataFrame({'x':[20.,10.]},index=[2,1]);pred=pd.DataFrame({'indice':[1,2]})
        self.assertEqual(aligned_predictions(model,pred,['x']).x.tolist(),[10.,20.])

    def test_duplicate_prediction_identifiers_rejected(self):
        with self.assertRaises(ValueError):
            aligned_predictions(pd.DataFrame({'x':[1.]},index=[1]),pd.DataFrame({'indice':[1,1]}),['x'])

    def test_unknown_prediction_identifier_rejected(self):
        with self.assertRaises(KeyError):
            aligned_predictions(pd.DataFrame({'x':[1.]},index=[1]),pd.DataFrame({'indice':[2]}),['x'])
