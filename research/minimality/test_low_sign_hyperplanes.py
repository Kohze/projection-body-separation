"""Proof coverage, boundary controls and deliberately corrupted certificates."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json,unittest
from flint import fmpz_mpoly_ctx
from check_low_sign_hyperplanes import cases,construct,density,verify

class LowSignHyperplanes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word='CCCCCCCAAC';cls.p=construct(10,2,cls.word)
        data=json.loads((Path(__file__).parent/'low-sign-hyperplane-certificates.json').read_text())
        cls.certificate=data['cases'][cls.word]

    def test_complete_order_cones(self):
        actual=cases();self.assertEqual(len(actual),46)
        self.assertEqual(actual[0],(1,None))
        self.assertEqual(len(set(word for k,word in actual if k==2)),45)
        self.assertTrue(all(word.count('A')==2 and word.count('C')==8 for k,word in actual if k==2))

    def test_difficult_cone_exact_certificate(self):
        result=verify(self.p,self.certificate)
        self.assertEqual(result['blocks'],986)
        self.assertEqual(result['circuit_blocks'],986)

    def test_corrupted_demand_rejected(self):
        bad=deepcopy(self.certificate);bad[0]['demand']=str(F(bad[0]['demand'])*2)
        with self.assertRaises(ValueError):verify(self.p,bad)

    def test_corrupted_exponent_rejected(self):
        bad=deepcopy(self.certificate);bad[0]['lower'][0]+=1
        with self.assertRaises(ValueError):verify(self.p,bad)

    def test_negative_polynomial_is_rejected(self):
        c=fmpz_mpoly_ctx.get(tuple('x'+str(i) for i in range(10)))
        with self.assertRaises(ValueError):verify(-c.gen(0)**2,[])

    def test_repeated_levels_density_and_polynomial(self):
        self.assertEqual(density([1,1],[1]*8),F(1,64))
        p=construct(10,2,'AACCCCCCCC')
        self.assertEqual(int(p(1,*([0]*9))),2**16*(9-F(32,64)))

    def test_multicoordinate_square(self):
        c=fmpz_mpoly_ctx.get(tuple('x'+str(i) for i in range(10)));x=c.gens()
        u=x[0]*x[3];v=x[1]*x[2]
        certificate=[dict(type='circuit',center=[1,1,1,1]+[0]*6,demand='4',
            lower=[2,0,0,2]+[0]*6,upper=[0,2,2,0]+[0]*6,
            lower_coefficient='2',upper_coefficient='2',upper_distance=1)]
        verify((u-v)**2,certificate)

if __name__=='__main__':unittest.main()
