"""Exact research checks for the dimension-eight minimality obstruction.

This is not a certificate of the unrestricted eight-dimensional inequality.
No external computer-algebra system or floating arithmetic is used in
proof acceptance. Sparse polynomial operations use exact integers.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
import argparse
import hashlib
import json
from math import factorial, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZERO = (0, 0, 0, 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(*polynomials):
    result = defaultdict(int)
    for p in polynomials:
        for powers, coefficient in p.items():
            result[powers] += coefficient
    return {powers: c for powers, c in result.items() if c}


def scale(p, c):
    return {powers: c * value for powers, value in p.items() if c * value}


def multiply(*polynomials):
    result = {ZERO: 1}
    for p in polynomials:
        out = defaultdict(int)
        for a, c in result.items():
            for b, d in p.items():
                out[tuple(x + y for x, y in zip(a, b))] += c * d
        result = {a: c for a, c in out.items() if c}
    return result


def power(p, n):
    return multiply(*([p] * n))


def variable(i):
    return {tuple(int(j == i) for j in range(4)): 1}


def decode(rows):
    result = {}
    for row in rows:
        powers = tuple(row['powers'])
        need(len(powers) == 4 and all(type(x) is int and x >= 0 for x in powers), 'Invalid powers')
        need(powers not in result, 'Duplicate monomial')
        need(type(row['coefficient']) is str, 'Invalid coefficient encoding')
        c = int(row['coefficient'])
        need(c != 0, 'Zero monomial')
        result[powers] = c
    return result


def substitute_ordered_gaps(p):
    gaps = [add(*(variable(j) for j in range(i + 1))) for i in range(4)]
    return add(*(scale(multiply(*(power(gaps[i], e) for i, e in enumerate(powers))), c)
                 for powers, c in p.items()))


def check_polynomial(data):
    u = [variable(i) for i in range(4)]
    one = {ZERO: 1}
    pairs = list(combinations(range(4), 2))
    denominator = multiply(*(add(one, x) for x in u), *(add(u[i], u[j]) for i, j in pairs))
    numerator = decode(data['numerator_terms'])
    need(denominator == decode(data['denominator_terms']), 'Wrong cleared denominator')
    vandermonde = multiply(*(add(u[i], scale(u[j], -1)) for i, j in pairs))
    # Clearing every factor in I = sum u_i^6 / ((1+u_i) prod_{j!=i}(u_i^2-u_j^2)).
    right = add(*(scale(multiply(power(u[i], 6),
                                  *(add(one, u[k]) for k in range(4) if k != i),
                                  *(add(power(u[j], 2), scale(power(u[k], 2), -1))
                                    for j, k in pairs if i not in (j, k))), (-1) ** i)
                  for i in range(4)))
    need(multiply(numerator, vandermonde) == right, 'Divided-difference identity failed')
    horizontal = add(scale(one, 9), *(scale(u[i], 2 * i + 1) for i in range(4)))
    difference = add(scale(denominator, 9), scale(multiply(horizontal, numerator), -1))
    gap_difference = substitute_ordered_gaps(difference)
    need(gap_difference == decode(data['gap_difference_terms']), 'Ordered-gap identity failed')
    need(gap_difference and all(c > 0 for c in gap_difference.values()), 'Unproved coefficient sign')
    return dict(denominator_monomials=len(denominator), numerator_monomials=len(numerator),
                ordered_gap_monomials=len(gap_difference), smallest_positive_coefficient=min(gap_difference.values()),
                degrees=sorted({sum(e) for e in gap_difference}))


def mean_gradient(v):
    """Derivative of E|sum v_i X_i|, X_i independent standard Laplace."""
    n = len(v)
    result = [F(0)] * n
    for i in range(n):
        term = v[i] ** (2 * n - 1) / prod(v[i] ** 2 - v[j] ** 2 for j in range(n) if i != j)
        for k in range(n):
            if k == i:
                result[k] += term * ((2 * n - 1) / v[i] - sum(2 * v[i] / (v[i] ** 2 - v[j] ** 2) for j in range(n) if i != j))
            else:
                result[k] += term * 2 * v[k] / (v[i] ** 2 - v[k] ** 2)
    return result


def paired_ratio(n, u):
    m = len(u)
    I = sum((u[i] ** (2 * m - 2) / ((1 + u[i]) * prod(u[i] ** 2 - u[j] ** 2 for j in range(m) if i != j)) for i in range(m)), F(0))
    P = n + 1 + sum((n - 2 * m + 2 * i + 1) * x for i, x in enumerate(u))
    return I * P / (n + 1)


def full_small_class():
    """Unpruned exact operation-state enumeration: no Pareto premise required."""
    g = [F(1)] + [F(n ** n, factorial(n)) for n in range(1, 10)]
    states = [{(F(1), F(1))}]
    rows = []
    for n in range(1, 10):
        out = set()
        for r in range(n):
            s = n - r - 1
            if r <= s:
                out.update((a + b, q * t) for a, q in states[r] for b, t in states[s])
            s = n - r
            if 0 < r <= s < n:
                for a, q in states[r]:
                    for b, t in states[s]:
                        out.add((n*a*b/(r*b+s*a), q*t*g[r]*g[s]/g[n]*(s*a+r*b)/n))
        states.append(out)
        maximum = max(h*q for h, q in out)
        need(maximum == n + 1, 'Small class has a nonsimplex maximum')
        rows.append(dict(dimension=n,distinct_states=len(out),R_over_simplex='1'))
    return rows


def product_envelope_corners():
    """Finite obligations for product closure of Q(H+8-n) <= 9.

    The difference is bilinear in H_A,H_B, so its minimum on the
    universal rectangle [1,r+1] x [1,s+1] is at a corner.
    """
    rows=[]
    for r in range(1,8):
        for s in range(r,9-r):
            n=r+s
            G=F(r**r,factorial(r))*F(s**s,factorial(s))/F(n**n,factorial(n))
            corners=[]
            for h in (F(1),F(r+1)):
                for j in (F(1),F(s+1)):
                    difference=(h+8-r)*(j+8-s)-9*G*(h*j+F(8-n,n)*(s*h+r*j))
                    need(difference>=9,'Product does not preserve the dimension-eight envelope')
                    corners.append(dict(H_left=str(h),H_right=str(j),difference=str(difference)))
            rows.append(dict(left_dimension=r,right_dimension=s,corners=corners))
    need(len(rows)==16,'Missing product dimension pair')
    return rows


def check():
    raw = (ROOT/'paired-eight-polynomial.json').read_bytes()
    polynomial = check_polynomial(json.loads(raw))
    gradient = mean_gradient(list(map(F, (1, 2, 4, 8))))
    need(gradient == [F(2749,18225), F(5304,18225), F(9624,18225), F(15664,18225)], 'Wrong supporting gradient')
    margins = [sum(gradient[k:]) - F(sum((1,3,5,7)[k:]), 9) for k in range(4)]
    need(all(x > 0 for x in margins), 'Ordered-cone bound failed')
    witness = paired_ratio(9, [F(x,100) for x in (1,2,3,5)])
    need(witness == F(20811283583,20797677600) and witness > 1, 'Wrong dimension-nine witness')
    return dict(status='PASS: exact arithmetic obligations',
                unrestricted_minimality_proved=False,
                paired_seed_family_first_separation_dimension=9,
                paired_seed_product_join_class_first_separation_dimension=9,
                polynomial_certificate_sha256=hashlib.sha256(raw).hexdigest(),
                polynomial=polynomial,analytic_anchor=[1,2,4,8],
                analytic_gradient=list(map(str,gradient)),ordered_cone_tail_margins=list(map(str,margins)),
                dimension_nine_R_over_simplex=str(witness),
                point_generated_class=full_small_class(),
                product_envelope_corners=product_envelope_corners(),
                class_calculus_attribution='mxym product/join calculus and exact finite-optima classification (2026); unpruned cross-check here',
                remaining_global_requirement='R_8(K) <= 131072/35 for every full-dimensional convex body K in R^8',
                analytic_scope='The note supplies the analytic proofs, continuity argument and inherited pyramid reduction. Finite arithmetic is not a formalization of those arguments.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,help='Optional output outside the delivered snapshot')
    parser.add_argument('--check-report',action='store_true',help='Compare with the delivered exact-arithmetic report')
    args=parser.parse_args()
    report=check()
    if args.check_report:
        need(report==json.loads((ROOT/'minimality-verification.json').read_text()),'Frozen report mismatch')
    encoded=json.dumps(report,indent=2)+'\n'
    if args.report:
        args.report.write_text(encoded,encoding='utf-8',newline='\n')
    print(encoded,end='')


if __name__=='__main__':
    main()
