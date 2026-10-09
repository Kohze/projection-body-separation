"""Produce explicit rational polytopes and pulling triangulations."""
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def pair(x):
    return [str(x.numerator), str(x.denominator)]


def determinant(rows):
    a = [list(row) for row in rows]
    sign = 1
    total = Fraction(1)
    for k in range(len(a)):
        p = next((i for i in range(k, len(a)) if a[i][k]), None)
        if p is None:
            return Fraction(0)
        if p != k:
            a[p], a[k] = a[k], a[p]
            sign = -sign
        pivot = a[k][k]
        total *= pivot
        for i in range(k + 1, len(a)):
            scale = a[i][k] / pivot
            for j in range(k + 1, len(a)):
                a[i][j] -= scale * a[k][j]
    return total * sign


def build(n, positive, denominator, name, output_directory=ROOT):
    m = len(positive)
    b = [-x for x in reversed(positive)] + positive + [0] * (n - 2*m)
    vertices = [[Fraction(0)] * n]
    # Put pyramid apices first so the pulling triangulation stays small.
    for i in list(range(2*m, n)) + list(range(2*m)):
        v = [Fraction(0)] * n
        v[i] = Fraction(denominator, denominator + abs(b[i]))
        vertices.append(v)
    for i in range(m):
        for j in range(m, 2*m):
            a = -b[i]
            p = b[j]
            v = [Fraction(0)] * n
            v[i] = Fraction(p, a + p)
            v[j] = Fraction(a, a + p)
            vertices.append(v)
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
    facets = [
        frozenset(
            i
            for i, v in enumerate(vertices)
            if sum(a * x for a, x in zip(row, v)) == rhs
        )
        for row, rhs in inequalities
    ]

    @lru_cache(None)
    def pulling(face):
        face = frozenset(face)
        if len(face) == 1:
            return [tuple(face)]
        pivot = min(face)
        candidates = {
            face & facet for facet in facets if face & facet and face & facet != face
        }
        maximal = [f for f in candidates if not any(f < g for g in candidates)]
        result = []
        for facet in sorted(maximal, key=lambda f: tuple(sorted(f))):
            if pivot not in facet:
                result.extend(
                    (pivot,) + simplex for simplex in pulling(tuple(sorted(facet)))
                )
        return result

    simplices = []
    for simplex in pulling(tuple(range(len(vertices)))):
        if len(simplex) != n + 1:
            raise ValueError("Pulling produced a wrong-dimensional simplex")
        rows = [
            [vertices[i][j] - vertices[simplex[0]][j] for j in range(n)]
            for i in simplex[1:]
        ]
        det = determinant(rows)
        if not det:
            raise ValueError("Degenerate simplex")
        simplex = list(simplex)
        if det < 0:
            simplex[-1], simplex[-2] = simplex[-2], simplex[-1]
        simplices.append(simplex)
    probe = [Fraction(1, 100 + i * i + 17 * i) for i in range(n)]
    data = {
        "format": "symmetric-two-facet-polytope-v2",
        "dimension": n,
        "parameter": ["1", str(denominator)],
        "tilt_coefficients": b,
        "vertices": [[pair(x) for x in v] for v in vertices],
        "oriented_simplices": simplices,
        "interior_probe": [pair(x) for x in probe],
        "construction": f"x_i >= 0; sum(({denominator}+b_i)*x_i) <= {denominator}; sum(({denominator}-b_i)*x_i) <= {denominator}",
        "attribution": "Symmetric central-section family motivated by Feng, Hu, Liu, and Xu (2026); recursive calculus credited to mxym (2026); priority not established.",
    }
    (output_directory / f"{name}.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {"dimension": n, "vertices": len(vertices), "simplices": len(simplices)}
        ),
        flush=True,
    )


if __name__ == "__main__":
    import argparse
    from exact_model import SEEDS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory', type=Path, default=ROOT)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    for name, (n, positive, denominator) in SEEDS.items():
        build(n, positive, denominator, name, args.output_directory)
