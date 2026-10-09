"""Generate a sparse inequality description by generic products and joins."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def product(body):
    dimension, rows = body
    return 2*dimension, [
        ([(i+shift, coefficient) for i, coefficient in terms], rhs)
        for shift in (0, dimension) for terms, rhs in rows
    ]


def join(body):
    dimension, rows = body
    result = []
    for side in (0, 1):
        for terms, rhs in rows:
            lifted = [(i+side*dimension, coefficient) for i, coefficient in terms]
            if rhs:
                lifted.append((2*dimension, rhs if side == 0 else -rhs))
            result.append((lifted, rhs if side == 0 else 0))
    return 2*dimension+1, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory', type=Path, default=ROOT)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    raw = (ROOT/'seed-twelve.json').read_bytes()
    seed = json.loads(raw)
    n = seed['dimension']; denominator = int(seed['parameter'][1]); tilts = seed['tilt_coefficients']
    rows = [([(i, -1)], 0) for i in range(n)]
    rows += [([(i, denominator+sign*t) for i,t in enumerate(tilts)], denominator) for sign in (1, -1)]
    body = (n, rows); vertices = len(seed['vertices'])
    for _ in range(2):
        body = join(product(body)); vertices = 2*vertices**2
    dimension, rows = body
    data = dict(schema='projection-recursive-block-inequalities-v1', dimension=dimension,
                facets=len(rows), vertices=vertices, seed_sha256=hashlib.sha256(raw).hexdigest(),
                recipe='K_2; K_(j+1)=(K_j x K_j)*(K_j x K_j)',
                inequalities=[dict(terms=terms,rhs=rhs) for terms,rhs in rows],
                interior_probe=[['1','400'] if i%49<48 else ['1','4'] for i in range(196)]+[['1','2']])
    (args.output_directory/'block-197.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(dimension=dimension,facets=len(rows),vertices=vertices)))


if __name__ == '__main__':
    main()
