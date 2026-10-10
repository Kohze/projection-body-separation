"""Adversarial geometry checks for the unrestricted candidate interface."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import unittest
import check_unrestricted as check

ROOT = Path(__file__).resolve().parent


class UnrestrictedChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = json.loads((ROOT/'unrestricted-examples.json').read_text())
        cls.polygon = next(row for row in cls.examples if row['dimension'] == 2)

    def test_exact_controls_and_scope(self):
        result = check.check()
        self.assertFalse(result['unrestricted_minimality_proved'])
        self.assertFalse(result['universal_dimension_eight_inequality_proved'])
        general = next(row for row in result['examples'] if row['name'] == 'three-upper-facets-eight')
        self.assertEqual(general['facets'], 11)
        self.assertEqual(F(general['section_cube_product']), F(general['R'])/8**8)

    def test_negative_orientation_rejected(self):
        data = deepcopy(self.polygon)
        data['oriented_simplices'][0][-1], data['oriented_simplices'][0][-2] = (
            data['oriented_simplices'][0][-2], data['oriented_simplices'][0][-1])
        with self.assertRaisesRegex(ValueError, 'orientation'):
            check.check_polytope(data)

    def test_missing_simplex_rejected(self):
        data = deepcopy(self.polygon)
        data['oriented_simplices'].pop()
        with self.assertRaises(ValueError):
            check.check_polytope(data)

    def test_duplicate_simplex_rejected(self):
        data = deepcopy(self.polygon)
        data['oriented_simplices'].append(data['oriented_simplices'][0])
        with self.assertRaisesRegex(ValueError, 'Repeated simplex'):
            check.check_polytope(data)

    def test_infeasible_point_rejected(self):
        data = deepcopy(self.polygon)
        data['points'][0][0] = ['-100', '1']
        with self.assertRaisesRegex(ValueError, 'Infeasible'):
            check.check_polytope(data)

    def test_duplicate_facet_rejected(self):
        data = deepcopy(self.polygon)
        data['halfspaces'].append(data['halfspaces'][0])
        with self.assertRaisesRegex(ValueError, 'unique boundary facet'):
            check.check_polytope(data)

    def test_boundary_probe_rejected(self):
        data = deepcopy(self.polygon)
        data['interior_probe'] = data['points'][0]
        with self.assertRaisesRegex(ValueError, 'strictly interior'):
            check.check_polytope(data)

    def test_residues_and_asymmetric_local_control(self):
        positive = check.exponential_statistics(range(1, 9))
        self.assertEqual(positive['p'], 1)
        self.assertEqual(positive['mean_abs'], 36)
        self.assertEqual(positive['simplex_ratio_derivative'], 0)
        result = check.exponential_statistics([-15, -11, -7, -3, 2, 5, 12, 17])
        self.assertLess(result['simplex_ratio_derivative'], 0)
        self.assertEqual(check.exponential_statistics([15, 11, 7, 3, -2, -5, -12, -17])['mean_abs'],
                         result['mean_abs'])


if __name__ == '__main__':
    unittest.main()
