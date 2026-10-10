"""Counterfeit certificates must fail on mathematical, not hash, grounds."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import check_minimality as check

ROOT=Path(__file__).resolve().parent


class MinimalityChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate=json.loads((ROOT/'paired-eight-polynomial.json').read_text())

    def test_exact_obligations_and_scope(self):
        result=check.check()
        self.assertFalse(result['unrestricted_minimality_proved'])
        self.assertEqual(result['paired_seed_family_first_separation_dimension'],9)
        self.assertEqual(result['paired_seed_product_join_class_first_separation_dimension'],9)
        self.assertEqual(len(result['product_envelope_corners']),16)
        self.assertEqual(result['point_generated_class'][-2]['distinct_states'],341)
        self.assertEqual(result['point_generated_class'][-1]['distinct_states'],914)

    def test_reject_false_divided_difference_numerator(self):
        data=deepcopy(self.certificate)
        data['numerator_terms'][0]['coefficient']=str(int(data['numerator_terms'][0]['coefficient'])+1)
        with self.assertRaisesRegex(ValueError,'Divided-difference'):
            check.check_polynomial(data)

    def test_reject_false_denominator(self):
        data=deepcopy(self.certificate)
        data['denominator_terms'].pop()
        with self.assertRaisesRegex(ValueError,'cleared denominator'):
            check.check_polynomial(data)

    def test_reject_missing_gap_monomial(self):
        data=deepcopy(self.certificate)
        data['gap_difference_terms'].pop()
        with self.assertRaisesRegex(ValueError,'Ordered-gap'):
            check.check_polynomial(data)

    def test_reject_false_positive_gap_expansion(self):
        data=deepcopy(self.certificate)
        data['gap_difference_terms'][0]['coefficient']='1000000000'
        with self.assertRaisesRegex(ValueError,'Ordered-gap'):
            check.check_polynomial(data)

    def test_reject_duplicate_monomial(self):
        data=deepcopy(self.certificate)
        data['numerator_terms'].append(data['numerator_terms'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            check.check_polynomial(data)

    def test_reject_invalid_exponent(self):
        data=deepcopy(self.certificate)
        data['numerator_terms'][0]['powers'][0]=-1
        with self.assertRaisesRegex(ValueError,'Invalid powers'):
            check.check_polynomial(data)


if __name__=='__main__':
    unittest.main()
