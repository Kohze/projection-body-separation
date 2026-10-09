"""Independent flattened-mass verification of the explicit block inequalities.

Does not import the producer or recursively construct products and joins.
Each of sixteen seed copies has an explicitly derived scale determined by
the four inner join coordinates and the one outer join coordinate.
"""
from collections import Counter
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(terms, rhs):
    require(type(rhs) is int, 'Noninteger support')
    require(type(terms) is list and len(terms)>0, 'Missing normal')
    indices = []
    for pair in terms:
        require(type(pair) in (list,tuple) and len(pair)==2, 'Invalid sparse term')
        index, value = pair
        require(type(index) is int and 0<=index<197 and type(value) is int and value!=0, 'Invalid sparse coefficient')
        indices.append(index)
    require(len(set(indices))==len(indices), 'Repeated coordinate')
    return tuple(sorted(map(tuple,terms))), rhs


def check(data, seed_bytes):
    seed = json.loads(seed_bytes)
    require(data.get('schema')=='projection-recursive-block-inequalities-v1', 'Wrong block schema')
    require(data.get('dimension')==197 and data.get('facets')==224 and data.get('vertices')==46118408, 'Wrong block dimensions/counts')
    require(data.get('seed_sha256')==hashlib.sha256(seed_bytes).hexdigest(), 'Wrong base seed')
    denominator = int(seed['parameter'][1]); b = seed['tilt_coefficients']
    require(seed['dimension']==12 and len(b)==12, 'Wrong base dimension')
    base = [([(i,-1)],0) for i in range(12)]
    base += [([(i,denominator+sign*t) for i,t in enumerate(b)],denominator) for sign in (1,-1)]
    expected = []
    for factor in range(4):
        inner = 49*factor+48
        for copy in range(4):
            offset = 49*factor+12*copy
            for terms, rhs in base:
                normal = [(offset+i,coefficient) for i,coefficient in terms]
                # Scale of copies 0,1: 1-T-z on the outer left,
                # T-z on the outer right. Scale of copies 2,3: z.
                if rhs:
                    normal.append((inner,rhs if copy<2 else -rhs))
                    if copy<2:
                        normal.append((196,rhs if factor<2 else -rhs))
                support = rhs if factor<2 and copy<2 else 0
                expected.append(canonical(normal,support))
    actual = [canonical(row['terms'],row['rhs']) for row in data['inequalities']]
    require(len(actual)==224 and Counter(actual)==Counter(expected), 'Inequalities do not equal the flattened recursive block')
    probe = [F(int(x[0]),int(x[1])) for x in data['interior_probe']]
    require(len(probe)==197, 'Wrong probe dimension')
    require(all(sum(probe[i]*coefficient for i,coefficient in terms)<rhs for terms,rhs in actual), 'Block probe is not strictly interior')
    return dict(status='PASS',dimension=197,facets=224,vertices=46118408,
                seed_copies=16,join_coordinates=5,inequalities_checked=len(actual),
                strict_interior_probe=True,scope='Exact H-representation equivalence to the certified recursive expression; no exhaustive vertex or volume enumeration')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=ROOT/'block-197-verification.json')
    args = parser.parse_args()
    raw = (ROOT/'block-197.json').read_bytes()
    report = check(json.loads(raw),(ROOT/'seed-twelve.json').read_bytes())
    report['certificate_sha256'] = hashlib.sha256(raw).hexdigest()
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
