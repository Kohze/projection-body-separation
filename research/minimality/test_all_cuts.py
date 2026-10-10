"""Fast tests of the local proof's recurrence and sign obligations."""
from fractions import Fraction as F
import unittest
import check_all_cuts as check


class AllCutsChecks(unittest.TestCase):
    def test_race_matches_independent_residues(self):
        self.assertEqual(len(check.controls()['independent_race_residue_comparisons']),12)

    def test_equal_exponential_race(self):
        self.assertEqual(check.race_moments([1],[1]),(F(1,2),F(1,2)))

    def test_nonpositive_means_rejected(self):
        with self.assertRaisesRegex(ValueError,'positive'):
            check.race_moments([0],[1])

    def test_invalid_sign_case_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid sign case'):
            check.construct(8,5)

    def test_small_polynomial(self):
        built=check.construct(4,2)
        checked=check.coefficient_obligation(built['polynomial'])
        self.assertEqual(checked['negative_coefficients'],0)
        self.assertEqual(checked['degree'],9)

    def test_counterfeit_negative_coefficient_rejected(self):
        built=check.construct(4,2)
        with self.assertRaisesRegex(ValueError,'not positive'):
            check.coefficient_obligation(built['polynomial']-1)

    def test_empty_polynomial_rejected(self):
        built=check.construct(4,1)
        with self.assertRaisesRegex(ValueError,'not positive'):
            check.coefficient_obligation(built['context'].constant(0))

    def test_one_negative_exact_factor(self):
        built=check.construct(4,1)
        self.assertEqual(built['removed_factor'](*[1,0,0,0]),1)
        self.assertGreater(built['polynomial'](*[1,1,0,0]),0)


if __name__=='__main__':unittest.main()
