BEYOND POINT-GENERATED PRODUCT--JOIN CONSTRUCTIONS
Internally audited research draft and exact reproduction package, 10 October 2026

VERSION 1.3.3 NOTE
Add a visible keywords line after the abstract and matching metadata.
The manuscript remains sixteen pages with twenty-one cited references.
Mathematical text, construction data and proof pins are unchanged.

VERSION 1.3.2 NOTE
The matching sixteen-page manuscript now cites twenty-one references.
Henk (2025) supplies recent geometric context; Ron (1988) receives the
classical exponential-spline attribution recorded by Xu. Precise formula
pointers are added. Mathematical certificates and proof pins are unchanged.

VERSION 1.3.1 NOTE
The matching sixteen-page manuscript has revised notation, numbered tables,
nineteen cited references and the same certified mathematical constants.
The current source/dependency ledger identifies all three asymptotic seed
families and the versioned release. Historical review records below retain
their original scope; the current internal review is in ../audit/.
The later sextic upper envelope is related work, not a substituted proof input.

VERSION 1.3.0 NOTE
The matching manuscript now has a stronger principal generic section seed
of dimension 18 and 23 facets, with amplified limit in (2.9280,2.9283).
Its analytic proof, integer columns and exact outward checker are in
../research/section-seeds/. From the repository root also run
  python -B research/section-seeds/check_section_seed.py --check-report
The symmetric polygon seed below remains included as a comparison.

VERSION 1.2.0 NOTE
The matching manuscript now has a stronger principal polygon-section seed
of dimension 15 and 18 facets, with amplified limit in (2.8900,2.8902).
Its analytic proof, exact data and independent checker are in
../research/polygon-seeds/. From the repository root also run
  python -B research/polygon-seeds/check_polygon_seed.py --check-report
The four two-upper-facet seed certificates and finite dimension-nine
comparison below remain valid and unchanged. This document describes
that original subsystem; it is not the complete v1.2.0 verification entry point.

Read beyond-point-generated.pdf for the mathematical argument and
PRIORITY_AND_DEPENDENCIES.txt for the contribution and source audit.
REVIEWER_AUDIT.txt gives the category scores, fixes, and remaining limits.
The matching editable TeX source is included.

RESULTS

Use h_(Pi K)(u)=vol_(n-1)(K projected onto u-perpendicular) and
R_n(K)=vol_n(Pi K)/vol_n(K)^(n-1).

The class C is generated from a point by finitely many Cartesian products,
joins, and invertible affine maps on affine hulls. It excludes rank-dropping
affine maps. The prior mixed Bellman theorem gives Gamma_C<=exp(1.049)<2.855.
The supplied successful replay concerns that attributed external theorem.

Our rational seed is
  K_0 = {x>=0: sum_i (100+B_i)x_i<=100;
                   sum_i (100-B_i)x_i<=100},
  B=(-69,-53,-41,-32,-24,-17,17,24,32,41,53,69).
It has dimension 12, 49 vertices, 14 facets, and a(K_0)=7/64.
Use the prior recursive operation
  K_(j+1)=(K_j x K_j)*(K_j x K_j).
Here x denotes Cartesian product and * denotes the canonical join in
independent coordinate spaces, as defined in the paper.

The exact certificates prove that R(K_j)^(1/dim K_j) strictly increases
to beta with 2.861<beta<2.8611. Simplex residue padding supplies an explicit
sequence in every dimension with the same limit. Thus this construction
has strictly larger exponential growth than the entire class C.

CURRENT FINITE SEPARATION: EVERY DIMENSION n>=9

The additional seed S_9 has paired tilts (1,2,3,5)/100 and one zero
coordinate; S_10 has paired tilts (16,51,91,142,217)/1000. They have
26 and 36 vertices. Their complete exact geometry is checked alongside
the original eight- and twelve-dimensional seeds.

threshold-recipes.json specifies 420 product/join nodes and W_n for every
integer n=9,...,245. threshold-certificate.json stores their exact H,Q
states. produce_threshold.py regenerates those states with the producer
formulas; check_threshold.py independently reconstructs them from geometry.

At n=9 the entire point-generated class has the simplex maximum c_9.
This prior Pareto result is independently replayed through n=9, checking
261 binary candidates and retaining 50 states across dimensions 0,...,9.
The seed satisfies R(S_9)/c_9=20811283583/20797677600>1.
Dimensions 10,...,48 are checked against rational tangent bounds for the
imported mixed Bellman envelope, with witness/upper bound >4001/4000.
For n>=49, the new analytic consequence of that envelope is
  sup_(K in C_n) R(K) < (9/10)*(7137/2500)^n.
Every base witness s=49,...,245 exceeds that bound by >1001/1000.
The existing block L=K_2, dimension 197, satisfies
  R(L) > (5/4)*(7137/2500)^197.
For n>=49 choose s=49+((n-49) mod 197), k=(n-s)/197, and set
  E_n = L^k x W_s.
Omit the factor L^0. Product multiplicativity proves separation in every
larger dimension. The finite certificate and analytic propagation cover
all n>=9, not only the finite verification range.

The older growth-certificate.json retains its successful dimension-15500
simplex-padding comparison as a historical control. The current result
is in threshold-verification.json. Nine is not proved minimal. Neither
this check nor the discovery search resolves unrestricted dimensions 4-8.

A simpler seed with B=(-4,-3,-2,-1,1,2,3,4) and denominator 10 has
dimension 8 and 25 vertices. Its root limit is between 2.8571 and 2.8573,
although its immediate R/c_8 ratio is below one.

For two seeds of the same dimension d, the specified recursion ranks their
limits exactly by a(K)*R(K)^3:
  (beta_A/beta_B)^(3d+1) = a(A)R(A)^3 / (a(B)R(B)^3).
For the symmetric tilt family this is the rational objective I^3*p^2*s.
This ranking does not optimize over arbitrary recursive schedules.

QUICK REPRODUCTION

Python 3.11 or newer; standard library only; no network required for all
new geometry and growth checks:
  python verify_all.py

This checks the delivery hashes, recomputes complete rational seed geometry,
compares the independently obtained R and a to the closed formulas, checks
the exact recursive states and infinite-tail hypotheses, checks all finite
separation constants, runs sixteen adversarial/unit tests, and checks regenerated
reports against their delivered hashes. Growth acceptance is replayed in
both normal and optimized Python. Typical runtime is around twenty seconds.

The runner writes regenerated reports and certificates to temporary files;
it leaves every delivered file unchanged. All sixteen unit tests also run under
optimized Python. Empty or incomplete manifests are rejected.

To regenerate the supplied certificates and confirm identical bytes:
  python verify_all.py --regenerate

The seed producer uses rational elimination and pulling triangulations.
The geometric checker independently enumerates active sets, uses fraction-
free determinants, verifies oriented-chain boundary cancellation and an
interior multiplicity, and computes actual facet and lifted minors. It does
not import the producer or exact_model.py. The growth checker reads the
regenerated geometric invariants and reconstructs the recurrence with
central binomial coefficients, rather than the producer's factorial ratios.

REPLAYING THE EXTERNAL UPPER THEOREM

The default runner verifies the existence and delivery integrity of the saved
successful prior replay; it does not silently rerun that external package.
To fetch and replay the pinned prior package:
  python replay_prior.py
or run everything with:
  python verify_all.py --with-prior

The first run needs network access. Exactly pinned files are downloaded to
.prior-cache and checked by SHA-256 and Git-blob SHA-1 before execution.
The optional fetch includes the prior package's own PDF because its delivery
manifest checks that file; third-party papers are not redistributed here.
The external checker then proves its finite obligations in ordinary Python.
The supplied record reports 19900 finite rectangles, 15568 tail cells, and
successful analytic-constant checks. Its analytic argument remains a cited
mathematical dependency, not something certified solely by replay.

Alternatively, point to an already downloaded matching flat package:
  python replay_prior.py --directory PATH_TO_PRIOR_PACKAGE

PDF BUILD

With a TeX installation containing the packages in the source:
  pdflatex -interaction=nonstopmode -halt-on-error beyond-point-generated.tex
  pdflatex -interaction=nonstopmode -halt-on-error beyond-point-generated.tex

Verify the delivered hashes before rebuilding. PDF metadata and TeX versions
can change PDF bytes. Byte-identical PDF regeneration is not claimed.

SCOPE

This is a working research draft, not an externally peer-reviewed result
or a proof-assistant formalization. The central geometric family, lifted
invariant, operation rules, recursion, tail method, and class upper bound are
prior work and are attributed in the paper and source audit. The certified
lower bounds and class separation are relative to the inspected sources;
bibliographic priority and unrestricted optimality are not established.
Numerical optimization guided seed selection but is not a proof dependency.
The dimension-197 block has an explicit 224-facet sparse integer description
in block-197.json, checked independently by check_block.py. Its 46,118,408
vertices are counted by the operation rules rather than enumerated. This
work does not resolve unrestricted dimensions 4 through 8. Research and
code were developed with AI assistance.

Older papers and archives in the surrounding workspace are preserved.
This package is a separate research continuation, with its own claims and
reproducibility records. Its manuscript, data and code edition is available at
https://github.com/Kohze/projection-body-separation/releases/tag/v1.3.0.
The original Python code and generated geometry/growth/block certificate data
are MIT licensed. Third-party inputs retain their upstream terms and are
fetched rather than redistributed. Manuscript rights are reserved separately.

VERSION 1.0.1 PORTABILITY FIX
The replay wrapper normalizes physical CRLF report line endings to LF. This
changes no JSON values or mathematical inputs; full report hashes are still
compared. A regression test covers Windows-style and Linux-style report bytes.
