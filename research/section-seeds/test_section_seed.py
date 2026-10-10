"""Check exact arithmetic controls and reject false geometric/growth claims."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json,unittest
import check_section_seed as checker


class SectionSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((Path(__file__).parent/'seed.json').read_text())

    def test_valid_seed_and_growth(self):
        report=checker.check(self.data)
        self.assertEqual(report['rays'][0]['genuine_facets_verified'],23)
        self.assertEqual(report['rays'][0]['all_affine_bases'],33649)
        self.assertFalse(report['unrestricted_minimality_proved'])

    def test_exact_determinant_controls(self):
        self.assertEqual(checker.determinant([[1,2,3],[0,4,5],[1,0,6]]),22)
        self.assertEqual(checker.determinant([[0,1],[3,2]]),-3)
        self.assertEqual(checker.determinant([[1,2],[2,4]]),0)

    def test_missing_column_rejected(self):
        bad=deepcopy(self.data);bad['columns'].pop()
        with self.assertRaises(ValueError):checker.check(bad)

    def test_false_seed_state_rejected(self):
        bad=deepcopy(self.data)
        bad['a_bounds']=[str(F(bad['a_bounds'][0])+F(1,1000)),str(F(bad['a_bounds'][1])+F(1,1000))]
        with self.assertRaises(ValueError):checker.check(bad)

    def test_non_generic_ray_rejected(self):
        bad=deepcopy(self.data);bad['rays'][0]=bad['columns'][0].copy()
        with self.assertRaises(ValueError):checker.check(bad)

    def test_false_lower_rate_rejected(self):
        bad=deepcopy(self.data);bad['limit_lower']='146411/50000'
        with self.assertRaises(ValueError):checker.check(bad)


if __name__=='__main__':unittest.main()
