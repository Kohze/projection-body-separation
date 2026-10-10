"""Adversarial checks of geometric coverage and claimed growth inputs."""
from copy import deepcopy
from fractions import Fraction as F
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import check_seeds
import check_growth
import verify_all
import check_block
import replay_prior
import check_threshold

ROOT = Path(__file__).resolve().parent


class CertificateChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT/'seed-eight.json').read_text())
        cls.growth = json.loads((ROOT/'growth-certificate.json').read_text())
        cls.geometry = {r['name']: r for r in json.loads((ROOT/'seed-geometry-verification.json').read_text())}
        cls.threshold = json.loads((ROOT/'threshold-certificate.json').read_text())
        cls.recipes = json.loads((ROOT/'threshold-recipes.json').read_text())

    def threshold_check(self, recipe=None, cert=None, geometry=None):
        recipe = deepcopy(self.recipes) if recipe is None else recipe
        cert = deepcopy(self.threshold) if cert is None else cert
        # Counterfeits below are allowed to recompute the recipe hash: the
        # mathematical checks, not merely the hash mismatch, must reject them.
        digest = hashlib.sha256(json.dumps(recipe).encode()).hexdigest()
        cert['recipe_sha256'] = digest
        return check_threshold.check(recipe, cert, self.geometry if geometry is None else geometry, digest)

    def test_dimension_nine_class_frontier_is_exact(self):
        result = check_threshold.exact_small_class(check_threshold.g_values(9))
        self.assertEqual(result['sharp_R_over_simplex'], '1')
        self.assertEqual(result['candidates_replayed'], 261)

    def test_threshold_rejects_a_simplex_in_small_dimensions(self):
        for n in (9, 18):
            recipe = deepcopy(self.recipes); cert = deepcopy(self.threshold)
            point = next(i for i, row in enumerate(recipe['nodes']) if row['op'] == ['point'])
            index = point
            for dimension in range(1, n+1):
                recipe['nodes'].append(dict(dimension=dimension, op=['join', point, index]))
                cert['nodes'].append(dict(dimension=dimension, H=str(dimension+1), Q='1'))
                index = len(recipe['nodes'])-1
            recipe['targets'][str(n)] = index
            with self.subTest(dimension=n), self.assertRaises(ValueError):
                self.threshold_check(recipe, cert)

    def test_threshold_rejects_missing_residue(self):
        recipe = deepcopy(self.recipes); recipe['targets'].pop('245')
        with self.assertRaisesRegex(ValueError, 'Missing dimension/residue'):
            self.threshold_check(recipe)

    def test_threshold_rejects_forged_state(self):
        cert = deepcopy(self.threshold); cert['nodes'][0]['Q'] = '1'
        with self.assertRaisesRegex(ValueError, 'False exact witness'):
            self.threshold_check(cert=cert)

    def test_threshold_rejects_wrong_block(self):
        cert = deepcopy(self.threshold); cert['block_R'] = '1'
        with self.assertRaisesRegex(ValueError, 'Wrong repeating block'):
            self.threshold_check(cert=cert)

    def test_threshold_rejects_false_seed_geometry(self):
        geometry = deepcopy(self.geometry); geometry['seed-ten']['Q'] = ['1', '1']
        with self.assertRaisesRegex(ValueError, 'False exact witness'):
            self.threshold_check(geometry=geometry)

    def test_seed_geometry_and_lifted_invariant(self):
        report = check_seeds.check(self.seed)
        self.assertEqual(report['vertices'], 25)
        self.assertEqual(report['positive_simplices_checked'], 70)
        self.assertEqual(report['scaled_projection_volume'], ['14', '1'])
        self.assertEqual(report['scaled_lifted_volume'], ['2', '1'])
        self.assertEqual(report['a'], ['1', '7'])

    def test_geometry_rejects_corrupt_certificates(self):
        cases = []
        bad = deepcopy(self.seed); bad['vertices'][0][0] = ['-1', '1']; cases.append(bad)
        bad = deepcopy(self.seed); bad['vertices'][1] = bad['vertices'][0]; cases.append(bad)
        bad = deepcopy(self.seed); bad['oriented_simplices'].pop(); cases.append(bad)
        bad = deepcopy(self.seed); bad['oriented_simplices'][0][:2] = reversed(bad['oriented_simplices'][0][:2]); cases.append(bad)
        bad = deepcopy(self.seed); bad['interior_probe'] = [['0', '1']]*8; cases.append(bad)
        for i, bad in enumerate(cases):
            with self.subTest(corruption=i), self.assertRaises(ValueError):
                check_seeds.check(bad)

    def test_growth_rejects_wrong_geometric_invariant(self):
        geometry = deepcopy(self.geometry)
        geometry['seed-twelve']['a'] = ['1', '2']
        with self.assertRaises(ValueError):
            check_growth.check(self.growth, geometry)

    def test_growth_rejects_wrong_geometric_volume(self):
        geometry = deepcopy(self.geometry)
        geometry['seed-twelve']['R'] = ['1', '1']
        with self.assertRaises(ValueError):
            check_growth.check(self.growth, geometry)

    def test_effective_comparison_rejects_insufficient_block(self):
        with self.assertRaises(ValueError):
            check_growth.check_effective(self.growth['effective_separation'], F(1))

    def test_exponential_bounds_are_rational(self):
        lo, hi = check_growth.exponential_interval(F(1))
        self.assertIsInstance(lo, F)
        self.assertIsInstance(hi, F)
        self.assertLess(F(1359, 500), lo)
        self.assertLess(hi, F(11, 4))

    def test_external_report_newlines_are_portable(self):
        payload = {'status': 'PASS', 'escaped': '\r\n', 'value': ['-3', '2000']}
        expected = (json.dumps(payload, indent=2)+'\n').encode()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'report.json'
            path.write_bytes(expected.replace(b'\n', b'\r\n'))
            replay_prior.normalize_report_newlines(path)
            self.assertEqual(path.read_bytes(), expected)
            self.assertEqual(json.loads(path.read_bytes()), payload)
            replay_prior.normalize_report_newlines(path)
            self.assertEqual(path.read_bytes(), expected)

    def test_manifest_rejects_missing_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'README.txt').write_text('fixture', encoding='utf-8')
            partial = hashlib.sha256((root/'README.txt').read_bytes()).hexdigest()+'  README.txt\n'
            with mock.patch.object(verify_all, 'ROOT', root):
                with self.assertRaises(ValueError):
                    verify_all.manifest()
                for contents in ('', partial, partial+partial):
                    (root/'ARTIFACTS.sha256').write_text(contents, encoding='utf-8')
                    with self.subTest(contents=contents), self.assertRaises(ValueError):
                        verify_all.manifest()

    def test_finite_bounds_reject_mathematically_false_claims(self):
        block = F(self.growth['families'][1]['levels'][2]['R'])
        for key, value in (('padding_constant', '1/1000'),
                           ('starting_dimension', 1000),
                           ('block_root_lower', '3'),
                           ('class_root_upper', '285479/100000')):
            bad = deepcopy(self.growth['effective_separation'])
            bad[key] = value
            with self.subTest(claim=key), self.assertRaises(ValueError):
                check_growth.check_effective(bad, block)

    def test_block_rejects_incorrect_inequalities_or_probe(self):
        original = json.loads((ROOT/'block-197.json').read_text())
        seed_bytes = (ROOT/'seed-twelve.json').read_bytes()
        cases = []
        bad = deepcopy(original); bad['inequalities'][-1]['terms'][-1][1] *= -1; cases.append(bad)
        bad = deepcopy(original); bad['inequalities'].pop(); cases.append(bad)
        bad = deepcopy(original); bad['interior_probe'][-1] = ['0','1']; cases.append(bad)
        for i,bad in enumerate(cases):
            with self.subTest(corruption=i), self.assertRaises(ValueError):
                check_block.check(bad, seed_bytes)


if __name__ == '__main__':
    unittest.main()
