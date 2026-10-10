"""Build finite controls for the unrestricted geometry checker.

Exhaustive active-set enumeration and pulling are construction procedures,
not assumptions of the independent positive-chain acceptance check.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import json
from check_unrestricted import det, dot, pair, solve, check_polytope

ROOT = Path(__file__).resolve().parent


def build(n, inequalities, name):
    inequalities = [(tuple(map(F, a)), F(h)) for a, h in inequalities]
    points = set()
    for subset in combinations(inequalities, n):
        vertex = solve([a for a, h in subset], [h for a, h in subset])
        if vertex is not None and all(dot(a, vertex) <= h for a, h in inequalities):
            points.add(vertex)
    points = sorted(points)
    facets = [frozenset(i for i, p in enumerate(points) if dot(a, p) == h)
              for a, h in inequalities]

    @lru_cache(None)
    def pulling(face):
        face = frozenset(face)
        if len(face) == 1:
            return [tuple(face)]
        pivot = min(face)
        intersections = {face & f for f in facets if face & f and face & f != face}
        maximal = [f for f in intersections if not any(f < g for g in intersections)]
        return [(pivot,)+s for f in sorted(maximal, key=lambda f: tuple(sorted(f)))
                if pivot not in f for s in pulling(tuple(sorted(f)))]

    simplices = []
    for raw in pulling(tuple(range(len(points)))):
        ids = list(raw)
        if len(ids) != n+1:
            raise ValueError('Wrong pulling dimension')
        base = points[ids[0]]
        determinant = det([[points[i][j]-base[j] for j in range(n)] for i in ids[1:]])
        if determinant < 0:
            ids[-1], ids[-2] = ids[-2], ids[-1]
        if not determinant:
            raise ValueError('Degenerate pulling simplex')
        simplices.append(ids)
    center = tuple(sum(p[j] for p in points)/len(points) for j in range(n))
    for trial in range(1, 101):
        probe = tuple(center[j]+F(trial**(j+1), 10**(2*n+5)) for j in range(n))
        if not all(dot(a, probe) < h for a, h in inequalities):
            continue
        generic = True
        for ids in simplices:
            base = points[ids[0]]
            rows = [[points[i][j]-base[j] for j in range(n)] for i in ids[1:]]
            bary = solve(list(zip(*rows)), [probe[j]-base[j] for j in range(n)])
            if not all(bary) or sum(bary) == 1:
                generic = False
                break
        if generic:
            break
    else:
        raise ValueError('No generic interior probe')
    result = dict(format='rational-halfspace-positive-chain-v1', name=name,
                  dimension=n,
                  halfspaces=[dict(normal=list(map(pair, a)), support=pair(h))
                              for a, h in inequalities],
                  points=[list(map(pair, p)) for p in points],
                  oriented_simplices=simplices, interior_probe=list(map(pair, probe)))
    checked = check_polytope(result)
    print(name, 'facets', checked['facets'], 'simplices', len(simplices),
          'simplex ratio', checked['simplex_ratio'], flush=True)
    return result


def orthant(n):
    return [([F(-int(i == j)) for j in range(n)], F(0)) for i in range(n)]


def main():
    examples = [build(8, orthant(8)+[([1]*8, 1)], 'simplex-eight')]
    for n, positive, denominator in [(8, [1, 2, 3, 4], 10), (9, [1, 2, 3, 5], 100)]:
        b = [-x for x in reversed(positive)]+positive+[0]*(n-8)
        upper = [([F(denominator+s*x, denominator) for x in b], F(1)) for s in (-1, 1)]
        examples.append(build(n, orthant(n)+upper, 'paired-'+('eight' if n == 8 else 'nine')))
    b = [-4, -3, -2, -1, 1, 2, 3, 4]
    c = [2, -4, 1, 3, -1, 4, -3, -2]
    upper = [([F(1)]*8, F(1))]+[([1+F(x, 10) for x in v], F(1)) for v in (b, c)]
    examples.append(build(8, orthant(8)+upper, 'three-upper-facets-eight'))
    asymmetric = [-15, -11, -7, -3, 2, 5, 12, 17]
    upper = [([1+F(s*x, 16000) for x in asymmetric], F(1)) for s in (-1, 1)]
    examples.append(build(8, orthant(8)+upper, 'asymmetric-centred-eight'))
    # An unrelated polygon exercises arbitrary facet incidence and n != 8,9.
    polygon = [([-1, 0], 0), ([0, -1], 0), ([1, 0], 3), ([0, 1], 3),
               ([1, 1], 5), ([2, -1], 5), ([-1, 2], 5)]
    examples.append(build(2, polygon, 'seven-facet-polygon'))
    target = ROOT/'unrestricted-examples.json'
    target.write_text(json.dumps(examples, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Wrote', target, flush=True)


if __name__ == '__main__':
    main()
