"""Exact controls for arbitrary-length hinge lists and their scope."""
from fractions import Fraction as F
import unittest
import check_zonotope_local as check
from check_unrestricted import exponential_statistics

class ZonotopeLocal(unittest.TestCase):
    def test_exact_controls_and_independent_distinct_knots(self):
        result=check.check();self.assertFalse(result['unrestricted_minimality_proved'])
        for row in result['hinges']:
            b=list(map(F,row['coefficients']));other=exponential_statistics(b)
            self.assertEqual(F(row['probability']),other['p'])
            self.assertEqual(F(row['positive_mean']),(other['mean_abs']+sum(b))/2)
            self.assertEqual(F(row['derivative_upper_bound']),other['simplex_ratio_derivative']/2)

    def test_repeated_coefficients(self):
        value=check.hinge_statistics([-1]*4+[1]*4)
        self.assertEqual(value['derivative_upper_bound'],F(-59,288))

    def test_zero_coefficients(self):
        self.assertEqual(check.hinge_statistics([-1,1]+[0]*6)['derivative_upper_bound'],F(-1,9))

    def test_linear_and_empty_deformations(self):
        self.assertEqual(F(check.check_hinges([])['derivative_upper_bound']),0)
        for b in ([0]*8,[1]*8,[-1]*8):
            self.assertEqual(F(check.check_hinges([b])['derivative_upper_bound']),0)

    def test_no_hinge_count_cap_but_dimension_eight_required(self):
        b=[-1,1]+[0]*6
        result=check.check_hinges([b]*100)
        self.assertEqual(result['hinge_count'],100)
        self.assertEqual(F(result['derivative_upper_bound']),F(-100,9))
        with self.assertRaises(ValueError):check.check_hinges([[-1,1]+[0]*7])

if __name__=='__main__':unittest.main()
