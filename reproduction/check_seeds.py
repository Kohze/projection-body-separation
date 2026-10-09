"""Independent exact geometry: vertices, triangulation, facets, projection volume.

Only the standard library is used. The triangulation is checked as a positive
oriented chain: all interior facets cancel, remaining faces lie on the body's
boundary, and one generic interior point has multiplicity one. This proves
coverage with no interior overlap by the path-crossing argument in the note.
"""
from collections import defaultdict
from fractions import Fraction
import argparse
import hashlib
import itertools
import json
from math import factorial, lcm, prod
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rational(raw):
    need(
        type(raw) is list and len(raw) == 2 and all(type(t) is str for t in raw),
        "Invalid rational encoding",
    )
    a, b = map(int, raw)
    need(b > 0, "Nonpositive denominator")
    return Fraction(a, b)


def bareiss(rows):
    a = [list(row) for row in rows]
    previous = 1
    sign = 1
    n = len(a)
    if n == 0:
        return 1
    for k in range(n - 1):
        if not a[k][k]:
            pivot = next((i for i in range(k + 1, n) if a[i][k]), None)
            if pivot is None:
                return 0
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        p = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * p - a[i][k] * a[k][j]
                need(numerator % previous == 0, "Non-exact determinant division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = p
    return sign * a[-1][-1]


def det(rows):
    scales = [lcm(*(x.denominator for x in row)) for row in rows]
    integers = [[int(x * s) for x in row] for row, s in zip(rows, scales)]
    return Fraction(bareiss(integers), prod(scales))


def solve(rows, rhs):
    n = len(rows)
    a = [[Fraction(x) for x in row] + [Fraction(y)] for row, y in zip(rows, rhs)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return None
        a[k], a[pivot] = a[pivot], a[k]
        p = a[k][k]
        for j in range(k, n + 1):
            a[k][j] /= p
        for i in range(n):
            if i != k and a[i][k]:
                scale = a[i][k]
                for j in range(k, n + 1):
                    a[i][j] -= scale * a[k][j]
    return tuple(a[i][-1] for i in range(n))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def check(data):
    need(data.get("format") == "symmetric-two-facet-polytope-v2", "Wrong witness format")
    n = data.get("dimension")
    need(type(n) is int and 2 <= n <= 30, "Unsupported dimension")
    parameter = rational(data.get("parameter"))
    need(parameter.numerator == 1, "Expected a reciprocal integer parameter")
    denominator = parameter.denominator
    b = data.get("tilt_coefficients")
    need(type(b) is list and len(b)==n and all(type(x) is int for x in b), "Invalid tilts")
    positive = sorted(x for x in b if x>0)
    need(positive and sorted(-x for x in b if x<0)==positive, "Tilt symmetry failed")
    need(len(set(positive))==len(positive) and max(positive)<denominator, "Unsupported tilts")
    m = len(positive)
    inequalities = []
    for i in range(n):
        row = [0] * n
        row[i] = -1
        inequalities.append((row, 0))
    inequalities.extend(
        [
            ([denominator + x for x in b], denominator),
            ([denominator - x for x in b], denominator),
        ]
    )
    raw = data.get("vertices")
    need(type(raw) is list and len(raw) == n + 1 + m*m, "Wrong vertex count")
    need(all(type(v) is list and len(v) == n for v in raw), "Wrong vertex dimension")
    vertices = [tuple(map(rational, v)) for v in raw]
    need(len(set(vertices)) == len(vertices), "Duplicate vertices")
    need(
        all(dot(a, v) <= rhs for a, rhs in inequalities for v in vertices),
        "Infeasible vertex",
    )
    # Independently enumerate all vertices from all n active inequalities.
    complete = set()
    active_systems = 0
    for subset in itertools.combinations(inequalities, n):
        active_systems += 1
        v = solve([a for a, r in subset], [r for a, r in subset])
        if v is not None and all(dot(a, v) <= rhs for a, rhs in inequalities):
            complete.add(v)
    need(set(vertices) == complete, "Incomplete or incorrect vertex list")
    probe = tuple(map(rational, data.get("interior_probe")))
    need(
        len(probe) == n and all(dot(a, probe) < rhs for a, rhs in inequalities),
        "Probe is not strictly interior",
    )
    simplices = data.get("oriented_simplices")
    need(
        type(simplices) is list and len(simplices) > 0, "Empty or invalid triangulation"
    )
    seen = set()
    boundary = defaultdict(int)
    detsum = Fraction(0)
    multiplicity = 0
    for ids in simplices:
        need(
            type(ids) is list
            and len(ids) == n + 1
            and all(type(i) is int and 0 <= i < len(vertices) for i in ids),
            "Invalid simplex",
        )
        need(
            len(set(ids)) == n + 1 and tuple(sorted(ids)) not in seen,
            "Repeated or invalid simplex",
        )
        seen.add(tuple(sorted(ids)))
        base = vertices[ids[0]]
        rows = [[vertices[i][j] - base[j] for j in range(n)] for i in ids[1:]]
        determinant = det(rows)
        need(determinant > 0, "Simplex orientation is not positive")
        detsum += determinant
        bary = solve(
            list(map(list, zip(*rows))), [probe[j] - base[j] for j in range(n)]
        )
        need(bary is not None, "Singular simplex")
        bary = (1 - sum(bary),) + bary
        need(all(bary), "Probe lies on a simplex face hyperplane")
        if all(x > 0 for x in bary):
            multiplicity += 1
        for omitted in range(n + 1):
            face = ids[:omitted] + ids[omitted + 1 :]
            inversions = sum(
                face[i] > face[j] for i in range(n) for j in range(i + 1, n)
            )
            boundary[tuple(sorted(face))] += (-1) ** (omitted + inversions)
    need(multiplicity == 1, "Triangulation does not have multiplicity one at the probe")
    volume = detsum / factorial(n)
    facet_vectors = [[Fraction(0)] * n for _ in inequalities]
    boundary_faces = 0
    for face, coefficient in boundary.items():
        if not coefficient:
            continue
        need(abs(coefficient) == 1, "Non-unit boundary multiplicity")
        facets = [
            i
            for i, (a, r) in enumerate(inequalities)
            if all(dot(a, vertices[v]) == r for v in face)
        ]
        need(
            len(facets) == 1,
            "Uncancelled face lies in the interior or on no unique facet",
        )
        index = facets[0]
        a, r = inequalities[index]
        axis = next(j for j in range(n) if a[j])
        base = vertices[face[0]]
        rows = [
            [vertices[v][j] - base[j] for j in range(n) if j != axis] for v in face[1:]
        ]
        minor = abs(det(rows))
        need(minor > 0, "Degenerate boundary simplex")
        scalar = minor / (factorial(n - 1) * abs(a[axis]))
        for j in range(n):
            facet_vectors[index][j] += scalar * a[j]
        boundary_faces += 1
    need(all(any(v) for v in facet_vectors), "A facet has no boundary coverage")
    need(
        all(sum(v[j] for v in facet_vectors) == 0 for j in range(n)),
        "Facet area vectors do not balance",
    )
    # Scaling all generators by the independently computed n*volume keeps
    # the exact determinants small; no formula for the facet areas is assumed.
    scale = n * volume
    generators = [[x / scale for x in v] for v in facet_vectors]
    projection_scaled = Fraction(0)
    minors = 0
    for subset in itertools.combinations(generators, n):
        projection_scaled += abs(det(subset))
        minors += 1
    projection_volume = scale**n * projection_scaled
    simplex = Fraction((n + 1) * factorial(n) ** (n - 1), factorial(n - 1) ** n)
    ratio = projection_volume / volume ** (n - 1) / simplex
    supports = []
    for generator, (normal, rhs) in zip(generators, inequalities):
        vertex = next(v for v in vertices if dot(normal,v)==rhs)
        supports.append(dot(generator,vertex))
    lifted = [list(v)+[h] for v,h in zip(generators,supports)]
    lifted_sum = sum((abs(det(subset)) for subset in itertools.combinations(lifted,n+1)),Fraction(0))
    invariant = lifted_sum / projection_scaled
    absolute_R = projection_volume / volume**(n-1)
    spectral_Q = invariant * absolute_R / Fraction(n**n,factorial(n))
    return {
        "dimension": n,
        "parameter": ["1", str(denominator)],
        "vertices": len(vertices),
        "facets": len(inequalities),
        "active_systems_checked": active_systems,
        "positive_simplices_checked": len(simplices),
        "uncancelled_boundary_simplices": boundary_faces,
        "interior_probe_multiplicity": multiplicity,
        "projection_minors_checked": minors,
        "polytope_volume": [str(volume.numerator), str(volume.denominator)],
        "scaled_projection_volume": [
            str(projection_scaled.numerator),
            str(projection_scaled.denominator),
        ],
        "ratio": [str(ratio.numerator), str(ratio.denominator)],
        "excess": [str((ratio - 1).numerator), str((ratio - 1).denominator)],
        "lifted_minors_checked": len(inequalities),
        "scaled_lifted_volume": [str(lifted_sum.numerator), str(lifted_sum.denominator)],
        "a": [str(invariant.numerator), str(invariant.denominator)],
        "R": [str(absolute_R.numerator), str(absolute_R.denominator)],
        "Q": [str(spectral_Q.numerator), str(spectral_Q.denominator)],
        "status": "explicit_rational_seed_geometry_verified",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT/'seed-geometry-verification.json')
    args = parser.parse_args()
    reports = []
    for name in ("seed-eight", "seed-twelve"):
        raw = (ROOT / f"{name}.json").read_bytes()
        start = time.monotonic()
        result = check(json.loads(raw))
        result["name"] = name
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        reports.append(result)
        print(
            json.dumps(
                {**result, "elapsed_seconds": round(time.monotonic() - start, 3)}
            ),
            flush=True,
        )
    args.report.write_text(
        json.dumps(reports, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
