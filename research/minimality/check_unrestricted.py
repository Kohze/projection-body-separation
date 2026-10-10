"""Exact geometry for arbitrary rational halfspace polytopes.

This checks individual certificates and the all-facet section identity; it
does not prove the universal dimension-eight inequality. The positive-chain
method and low-level rational determinant arithmetic are adapted from the
repository's MIT-licensed reproduction/check_seeds.py. No paired-seed,
facet-count, simple-polytope or optimizer assumption enters acceptance.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
from math import comb, factorial, lcm, prod
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pair(x):
    return [str(x.numerator), str(x.denominator)]


def rational(raw):
    need(type(raw) is list and len(raw) == 2 and
         all(type(x) is str for x in raw), 'Invalid rational encoding')
    a, b = map(int, raw)
    need(b > 0, 'Nonpositive denominator')
    return F(a, b)


def det(rows):
    if not rows:
        return F(1)
    scales = [lcm(*(F(x).denominator for x in row)) for row in rows]
    a = [[int(x*s) for x in row] for row, s in zip(rows, scales)]
    previous = sign = 1
    n = len(a)
    for k in range(n-1):
        if not a[k][k]:
            p = next((i for i in range(k+1, n) if a[i][k]), None)
            if p is None:
                return F(0)
            a[k], a[p] = a[p], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = a[i][j]*pivot-a[i][k]*a[k][j]
                need(numerator % previous == 0, 'Non-exact Bareiss division')
                a[i][j] = numerator//previous
            a[i][k] = 0
        previous = pivot
    return F(sign*a[-1][-1], prod(scales))


def solve(rows, rhs):
    n = len(rows)
    a = [[F(x) for x in row]+[F(y)] for row, y in zip(rows, rhs)]
    for k in range(n):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return None
        a[k], a[p] = a[p], a[k]
        pivot = a[k][k]
        a[k] = [x/pivot for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                scale = a[i][k]
                a[i] = [x-scale*y for x, y in zip(a[i], a[k])]
    return tuple(row[-1] for row in a)


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def check_polytope(data):
    need(data.get('format') == 'rational-halfspace-positive-chain-v1', 'Wrong format')
    n = data.get('dimension')
    need(type(n) is int and n >= 2, 'Invalid dimension')
    inequalities = []
    for row in data['halfspaces']:
        a = tuple(map(rational, row['normal']))
        need(len(a) == n and any(a), 'Invalid halfspace normal')
        inequalities.append((a, rational(row['support'])))
    m = len(inequalities)
    need(m >= n+1, 'Too few halfspaces')
    points = [tuple(map(rational, row)) for row in data['points']]
    need(points and all(len(p) == n for p in points), 'Invalid point dimension')
    need(len(points) == len(set(points)), 'Duplicate points')
    need(all(dot(a, p) <= h for a, h in inequalities for p in points),
         'Infeasible point')
    probe = tuple(map(rational, data['interior_probe']))
    need(len(probe) == n and all(dot(a, probe) < h for a, h in inequalities),
         'Probe is not strictly interior')
    simplices = data['oriented_simplices']
    need(type(simplices) is list and simplices, 'Empty or invalid chain')
    boundary = defaultdict(int)
    seen = set()
    detsum = F(0)
    multiplicity = 0
    for ids in simplices:
        need(type(ids) is list and len(ids) == n+1 and
             all(type(i) is int and 0 <= i < len(points) for i in ids), 'Invalid simplex')
        key = tuple(sorted(ids))
        need(len(set(ids)) == n+1 and key not in seen, 'Repeated simplex')
        seen.add(key)
        base = points[ids[0]]
        rows = [[points[i][j]-base[j] for j in range(n)] for i in ids[1:]]
        determinant = det(rows)
        need(determinant > 0, 'Simplex orientation is not positive')
        detsum += determinant
        bary = solve(list(zip(*rows)), [probe[j]-base[j] for j in range(n)])
        need(bary is not None, 'Singular simplex')
        bary = (1-sum(bary),)+bary
        need(all(bary), 'Probe lies on a simplex face hyperplane')
        multiplicity += int(all(x > 0 for x in bary))
        for omitted in range(n+1):
            face = ids[:omitted]+ids[omitted+1:]
            inversions = sum(face[i] > face[j] for i in range(n) for j in range(i+1, n))
            boundary[tuple(sorted(face))] += (-1)**(omitted+inversions)
    need(multiplicity == 1, 'Chain does not have probe multiplicity one')
    volume = detsum/factorial(n)
    area = [[F(0)]*n for _ in inequalities]
    supports = [None]*m
    boundary_count = 0
    for face, coefficient in boundary.items():
        if not coefficient:
            continue
        need(abs(coefficient) == 1, 'Non-unit boundary multiplicity')
        active = [i for i, (a, h) in enumerate(inequalities)
                  if all(dot(a, points[v]) == h for v in face)]
        need(len(active) == 1, 'Uncancelled face has no unique boundary facet')
        i = active[0]
        a, h = inequalities[i]
        axis = next(j for j in range(n) if a[j])
        base = points[face[0]]
        projected = [[points[v][j]-base[j] for j in range(n) if j != axis]
                     for v in face[1:]]
        minor = abs(det(projected))
        need(minor > 0, 'Degenerate boundary simplex')
        scale = minor/(factorial(n-1)*abs(a[axis]))
        for j in range(n):
            area[i][j] += scale*a[j]
        supports[i] = points[face[0]]
        boundary_count += 1
    need(all(any(u) for u in area), 'A halfspace has no facet coverage')
    need(all(sum(u[j] for u in area) == 0 for j in range(n)), 'Unbalanced area vectors')
    z = [dot(u, p) for u, p in zip(area, supports)]
    need(sum(z) == n*volume, 'Divergence identity failed')
    T = [[-x/(n*volume) for x in u] for u in area]
    lam = [(h-dot(u, probe))/(n*volume) for h, u in zip(z, area)]
    need(all(x > 0 for x in lam) and sum(lam) == 1, 'Invalid section offset')
    need(all(sum(row[j] for row in T) == 0 for j in range(n)), 'Section not in one-perp')
    gram = [[sum(row[i]*row[j] for row in T) for j in range(n)] for i in range(n)]
    gram_det = det(gram)
    need(gram_det > 0, 'Section map lacks full rank')
    minors = sum((abs(det(subset)) for subset in combinations(T, n)), F(0))
    # Both Euclidean factors can be irrational; their product is rational.
    section_sq = gram_det*volume**2
    cube_sq = minors**2/gram_det
    section_cube = volume*minors
    need(section_sq*cube_sq == section_cube**2, 'Section-cube identity failed')
    projection = (n*volume)**n*minors
    R = projection/volume**(n-1)
    need(section_cube == R/n**n, 'Projection normalization failed')
    ratio = section_cube*factorial(n)/(n+1)
    return dict(name=data.get('name', ''), dimension=n, facets=m,
                points=len(points), positive_simplices=len(simplices),
                boundary_simplices=boundary_count, probe_multiplicity=multiplicity,
                volume=str(volume), projection_volume=str(projection), R=str(R),
                simplex_ratio=str(ratio), section_cube_product=str(section_cube),
                section_volume_squared=str(section_sq), cube_projection_volume_squared=str(cube_sq),
                gram_determinant=str(gram_det), offset=list(map(str, lam)),
                projection_minor_count=comb(m, n),
                status='PASS: individual exact geometry and all-facet identity',
                universal_bound_proved=False)


def exponential_statistics(b):
    """Distinct nonzero knots; expectation of positive part by residues."""
    b = list(map(F, b))
    need(len(b) == len(set(b)) and all(b), 'Expected distinct nonzero coefficients')
    n = len(b)
    p = positive_mean = F(0)
    gradient = [F(-1)]*n
    for i, x in enumerate(b):
        if x < 0:
            continue
        denominator = prod(x-y for j, y in enumerate(b) if i != j)
        p += x**(n-1)/denominator
        term = x**n/denominator
        positive_mean += term
        for k, y in enumerate(b):
            gradient[k] += 2*term*(F(n, 1)/x-sum(1/(x-z) for j, z in enumerate(b) if i != j)
                                   if k == i else 1/(x-y))
    mean_abs = 2*positive_mean-sum(b)
    dispersion = sum(abs(x-y) for x, y in combinations(b, 2))
    derivative = -mean_abs+(2*p-1)*sum(b)+2*p*(1-p)*dispersion/(n+1)
    return dict(p=p, mean_abs=mean_abs, gradient=gradient, D=dispersion,
                simplex_ratio_derivative=derivative)


def check_first_variation():
    anchor = [-8, -4, -2, -1, 1, 2, 4, 8]
    values = exponential_statistics(anchor)
    gradient = values['gradient']
    expected = [F(x, 36450) for x in (-15664, -9624, -5304, -2749,
                                     2749, 5304, 9624, 15664)]
    need(gradient == expected and values['p'] == F(1, 2), 'Wrong exponential gradient')
    differences = [gradient[i]-F(2*i-7, 18) for i in range(8)]
    need(sum(differences) == 0, 'Supporting difference is not translation invariant')
    margins = [sum(differences[j:]) for j in range(1, 8)]
    expected_margins = [F(x, 36450) for x in (1489, 988, 217, 941, 217, 988, 1489)]
    need(margins == expected_margins and min(margins) > 0, 'Ordered-cone margin failed')
    radius = F(1, 500)
    # For 0<=s<=radius, ((1-s)^(-2)-1)/s is increasing.
    need((2-radius)/(1-radius)**2 <= F(201, 100), 'Finite-radius transform bound failed')
    quadratic = 1+F(8, 9)*F(201, 100)
    need(quadratic == F(209, 75), 'Wrong quadratic remainder')
    deficit = min(margins)-quadratic*radius
    need(deficit >= F(1, 3000), 'Finite-radius strict deficit failed')
    asymmetric = exponential_statistics([-15, -11, -7, -3, 2, 5, 12, 17])
    need(asymmetric['simplex_ratio_derivative'] < 0, 'Asymmetric control failed')
    return dict(anchor=anchor, gradient=list(map(str, gradient)),
                ordered_gap_margins=list(map(str, margins)),
                strict_derivative_margin='217/36450 times the coefficient range',
                finite_radius=str(radius), finite_ratio_deficit='coefficient range / 3000',
                finite_deficit_coefficient=str(deficit), quadratic_remainder=str(quadratic),
                scope='All centered coefficient vectors in dimension eight; strict derivative and finite coefficient range <= 1/500',
                asymmetric_control={k: str(v) for k, v in asymmetric.items() if k != 'gradient'},
                universal_bound_proved=False)


def check():
    data = json.loads((ROOT/'unrestricted-examples.json').read_text())
    examples = [check_polytope(row) for row in data]
    expected = {'simplex-eight': F(1), 'paired-eight': F(231953, 243243),
                'paired-nine': F(20811283583, 20797677600)}
    for row in examples:
        if row['name'] in expected:
            need(F(row['simplex_ratio']) == expected[row['name']], 'Known geometry control failed')
        if row['name'] == 'asymmetric-centred-eight':
            need(F(row['simplex_ratio']) <= 1-F(1, 1500000), 'Finite asymmetric control failed')
    return dict(status='PASS: all-facet identity and local arithmetic obligations',
                universal_dimension_eight_inequality_proved=False,
                unrestricted_minimality_proved=False, examples=examples,
                first_variation=check_first_variation())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, help='Check an individual arbitrary-polytope certificate')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--check-report', action='store_true')
    args = parser.parse_args()
    result = check_polytope(json.loads(args.certificate.read_text())) if args.certificate else check()
    if args.check_report:
        need(result == json.loads((ROOT/'unrestricted-verification.json').read_text()), 'Frozen report mismatch')
    output = json.dumps(result, indent=2)+'\n'
    if args.report:
        args.report.write_text(output, encoding='utf-8', newline='\n')
    print(output, end='')


if __name__ == '__main__':
    main()
