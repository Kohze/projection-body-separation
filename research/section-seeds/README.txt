GENERIC RATIONAL SIMPLEX-SECTION SEED -- VERSION 1.3.0

The principal seed is S={x>=0: sum x_i=1, Bx=0}, where seed.json specifies
23 integer columns of B in R^4. Its dimension is 18 and all 23 coordinate
facets are genuine. Product-join amplification has root limit
  2.9280 < beta < 2.9283.
The preceding simpler polygon seed with limit above 2.890 remains in
../polygon-seeds/ as an exact comparison and a compact symmetric example.

From the repository root, with Python 3.11 or newer:
  python -B research/section-seeds/check_section_seed.py --check-report
  python -B -m unittest discover -s research/section-seeds -p 'test_*.py' -v
  python -B -O -m unittest discover -s research/section-seeds -p 'test_*.py' -v

The standard-library checker verifies all 8855 linear and 33649 affine
bases and proves the coordinate-facet hypotheses by exact barycentric
signs. It computes density and gradient sums on two generic rays and
encloses them by integer arithmetic at precision 256 bits. The facet
weights and their products are enclosed outwards at precision 128 bits.
The resulting state bounds and the infinite-limit endpoints are rigorous;
floating-point optimization is not an acceptance premise.

proof.txt proves the geometric state formulas and explains the classical
multivariate interpolation identity. General position proves that identity
by an interpolation basis argument; no sampled identity or enormous
coefficient list is trusted. The inherited analytic tail proof uses upper
constant 8 for this seed. Six adversarial/regression tests include false
state and false asymptotic-bound inputs.

--check-report leaves delivered files unchanged; omitting it regenerates
verification.json. Each check takes a few seconds. The output records
enclosures, not floating approximations or a claim of exact equality to a
truncated value. Algorithmic reconstruction does not replace mathematical
review of proof.txt and the imported calculus.

The simplex-section and complementary-minor methods are attributed to
Feng, Hu, Liu and Xu (2026), and the spline/Laplace approach is classical;
see Z. Xu, Multivariate splines and polytopes, J. Approx. Theory 163 (2011),
377-387, doi:10.1016/j.jat.2010.10.005. The lifted invariant, operation
rules, amplification scheme and comparison upper theorem remain attributed
to mxym. The contribution is this specified seed and stronger certified
rate. Global optimality, unrestricted minimality and bibliographic
priority remain unproved. Original code/data: MIT, under LICENSE.
