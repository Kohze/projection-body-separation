"""Adversarial checks for the new seed's exact acceptance boundary."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json,unittest
import check_polygon_seed as checker


class SeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((Path(__file__).parent/'seed.json').read_text())

    def test_exact_seed_and_limit(self):
        result=checker.check(self.data)
        self.assertEqual(result['a'],'1/9')
        self.assertEqual(result['R_over_g'],'4877231181816111466/252095850530248725')
        self.assertFalse(result['unrestricted_minimality_proved'])

    def test_missing_coordinate_rejected(self):
        bad=deepcopy(self.data);bad['columns'].pop()
        with self.assertRaises(ValueError):checker.check(bad)

    def test_broken_orbit_rejected(self):
        bad=deepcopy(self.data);bad['columns'][1][0]='71/10'
        with self.assertRaises(ValueError):checker.check(bad)

    def test_wrong_density_rejected(self):
        bad=deepcopy(self.data);bad['density']=str(F(bad['density'])+F(1,1000))
        with self.assertRaises(ValueError):checker.check(bad)

    def test_overclaimed_lower_limit_rejected(self):
        bad=deepcopy(self.data);bad['limit_lower']='289019/100000';bad['limit_upper']='14451/5000'
        with self.assertRaises(ValueError):checker.check(bad)


if __name__=='__main__':unittest.main()
