RATIONAL POLYGON-SECTION SEED -- VERSION 1.2.0

The principal seed is the 15-dimensional rational polytope
  S={x>=0: sum x_i=1, Bx=0},
where the 18 columns of B are A^j(10,0), A^j(7,4), A^j(4,7), 0<=j<6,
and A(x,y)=(-y,x+y). Integer coordinates are in seed.json.

The inherited recursion (K x K)*(K x K) has a strictly increasing root
sequence with limit beta satisfying 2.8900<beta<2.8902. This strengthens
the preceding certified lower endpoint 2.861. It does not prove global
optimality, bibliographic priority, or the minimal separation dimension.

From the repository root, using Python 3.11 or newer:
  python -B research/polygon-seeds/check_polygon_seed.py --check-report
  python -B -m unittest discover -s research/polygon-seeds -p 'test_*.py' -v
  python -B -O -m unittest discover -s research/polygon-seeds -p 'test_*.py' -v

Only the standard library is used. The checker reconstructs all columns,
facet hypotheses, determinant sums, and the density from a full rational
Laplace-transform identity. It independently checks three generic rays,
regenerates the exact recursion through dimension 15701, and compares
integer powers to certify both infinite-limit endpoints. Floating-point
search and numerical optimizer success are not acceptance premises.
--check-report leaves delivered files unchanged; omit it to regenerate
verification.json. Five tests include false-state and false-bound inputs.

proof.txt and Section 4 of the paper explain why these finite identities
establish the geometric result. Algorithmic checks do not replace review
of that analytic argument or the attributed product-join calculus.

The simplex-section method is attributed to Feng, Hu, Liu and Xu (2026).
The spline volume/Laplace method is classical; see Z. Xu, Multivariate
splines and polytopes, J. Approx. Theory 163 (2011), 377-387,
doi:10.1016/j.jat.2010.10.005. The operation rules, lifted invariant,
amplification scheme and class upper bound remain attributed to mxym.
No novelty is claimed for these tools or for polygon/Gale constructions.
The additional contribution is the specified seed and stronger bound.

Targeted prior-art audit, 10 October 2026: checked the Feng manuscript,
Xu's spline work, relevant web searches, and 123 projection/product-join
texts from the current mxym upstream tree at commit 4248c2b2d4.
No matching seed or amplified bound was located in that inspected corpus.
This is bounded search evidence, not a proof of global priority.

Original code/data: MIT, under the repository LICENSE. The same AI
disclosure as the companion papers appears in the main manuscript.
