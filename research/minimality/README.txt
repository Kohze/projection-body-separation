DIMENSION-NINE MINIMALITY RESEARCH SUPPLEMENT
10 October 2026

Proved in this supplement:
  * Global minimality of dimension 9 is equivalent to the unrestricted
    simplex bound R_8(K) <= 131072/35 for every eight-dimensional convex body.
  * Dimension 9 is the first separation dimension within the paired
    two-upper-facet seed family and its entire closure under products,
    joins and affine maps. The class is defined precisely in minimality.tex.
  * A short analytic proof and a separate positive-polynomial certificate
    establish the dimension-eight family bound.
  * An equivalent unrestricted section-projection inequality retains every
    facet count m >= 9; no reduction to a bounded number of facets is made.
  * Centred, possibly asymmetric two-upper-facet cuts in dimension eight
    strictly lower the simplex ratio when the tilt range is at most 1/500.
    The ratio is at most 1 minus the tilt range divided by 3000.
  * Every two-upper-facet direction K_epsilon(b) in dimension eight has
    nonpositive first variation at the simplex, without centring. It is
    strictly negative when both signs are present and all coefficients are
    nonzero, including repeated levels. This is a computer-assisted local
    theorem, not a bound for arbitrary finite deformations.

NOT proved:
  Global minimality over all convex bodies. General asymmetric seeds and
  arbitrary bodies are not reduced to the class generated from paired
  seeds. A finite search is not a nonexistence proof.

This is a research supplement to the v1.1.0 paper. It does not replace
that versioned paper or its sealed reproduction snapshot. Analytic proofs
are not proof-assistant formalized or externally peer reviewed.

FILES
  minimality.tex / minimality.pdf   Human-readable mathematical arguments.
  paired-eight-polynomial.json     Exact integer polynomial certificate.
  check_minimality.py              Independent standard-library checker.
  minimality-verification.json     Frozen output of exact obligations.
  test_minimality.py               Seven positive and adversarial tests.
  build_note.py                   Rebuild without leaving TeX auxiliary files.
  check_unrestricted.py           General rational-polytope geometry checker.
  unrestricted-examples.json      Six finite geometric controls.
  unrestricted-verification.json  Exact section identity and local constants.
  build_unrestricted_examples.py  Reconstruct the finite geometric controls.
  test_unrestricted.py            Eight geometry and arithmetic tests.
  check_all_cuts.py               Exact polynomial proof for all sign cases.
  all-cuts-verification.json      Counts and rational controls for that proof.
  requirements-all-cuts.txt       Pinned optional python-flint dependency.
  test_all_cuts.py                Eight tests for the polynomial proof code.

REPRODUCE (Python 3.11 or newer; no network or third-party dependencies)
  python -B check_minimality.py --check-report
  python -B -m unittest -v test_minimality.py
  python -B -O -m unittest -v test_minimality.py
  python -B check_unrestricted.py --check-report
  python -B -m unittest -v test_unrestricted.py
  python -B -O -m unittest -v test_unrestricted.py

These commands do not modify delivered files. The optional --report PATH
flag writes the regenerated exact-arithmetic report to a path of your choice.
The checker reconstructs sparse polynomials from integer factors, proves
the cleared divided-difference identity, expands ordered gaps and checks
all 585 positive coefficients. It separately computes a supporting gradient
checks all 64 corner obligations for product closure of the finite envelope,
and enumerates unpruned product/join states through dimension 9. The
operation calculus is attributed prior work; the note supplies the analytic
reasoning that finite arithmetic alone cannot replace.

ALL TWO-FACET FIRST VARIATIONS (optional third-party dependency)
  python -m pip install -r requirements-all-cuts.txt
  python -B check_all_cuts.py --check-report
  python -B -m unittest -v test_all_cuts.py
  python -B -O -m unittest -v test_all_cuts.py

This proof reconstructs integer polynomials for all four mixed-sign cases,
expands ordered gaps, and checks all 17,265,590 nonzero coefficients, each
positive. It also checks repeated-level strictness, twelve independent
rational race/residue controls and a dimension-nine positive control. Zero
coefficients are handled by the continuity argument in the manuscript.
Installation needs network access unless the package is already available;
the proof itself does not. Allow several minutes and several gigabytes of
memory for the full check. No numerical search is a proof premise. Exact
FLINT arithmetic is a software dependency, not a proof-assistant kernel or
an independent implementation. This part contributes 23 supplement tests;
the later low-sign extension adds seven.

GENERAL CANDIDATE INTERFACE
  python -B check_unrestricted.py --certificate PATH

The input format is illustrated by each object in unrestricted-examples.json:
rational halfspaces, feasible points, positively oriented simplices, and a
generic interior probe. Rational numbers use [numerator, denominator] strings.
The checker requires a nonredundant facet list, but does not require paired
coefficients, a simple polytope, or a bounded number of facets. Acceptance uses
positive-chain coverage, facet-area vectors, balance, divergence and exact
minors. It reconstructs a simplex section from any accepted polytope and
checks vol(section)*vol(cube projection) = R_n(K)/n^n. Squared Euclidean
volumes avoid rounding irrational square roots. The generator enumerates
active sets and constructs pulling triangulations; acceptance checks their
geometry rather than trusting that construction algorithm.

Individual checks and the local centred-cut theorem do not prove the full
dimension-eight inequality. In particular, a fixed facet-count search or a
negative first variation cannot establish global minimality. Recent simplex
slicing bounds control section volume; the remaining target couples it to
the cube projection volume and quantifies over all ambient dimensions.

BUILD PDF (pdflatex and the packages declared in the source required)
  python -B build_note.py

The original paper's reproduction/verify_all.py also checks the dimension-nine
witness from its exact geometry. Those checks are separate from this
supplement's symbolic polynomial and supporting-gradient obligations.

RIGHTS
  Original checker code and certificate data use the repository's MIT license.
  Manuscript rights follow RIGHTS.md. Third-party inputs are linked and
  attributed, not redistributed. No global novelty or priority claim is made.

ALL-OFFSET LOW-SIGN HYPERPLANE FAMILY (additional executable research result)

This result extends the research package after the current supplement PDF.
It proves the following finite-family statement, not global minimality:

  For b in R^10 with both signs present and with at most two coefficients
  of one sign, let Z=sum_i b_i X_i for independent mean-one exponentials,
  and D(b)=sum_{i<j}|b_i-b_j|. Then D(b)*f_Z(0) <= 9.

Zero coefficients follow by approximation within this family. Holding one
nonzero coefficient of each sign fixed gives a continuous bounded Laplace
density; convolution and dominated convergence establish continuity at zero.
Reflection handles the cases with at most two positive coefficients.

Geometric reduction (attributed): Feng, Hu, Liu and Xu, On the Reverse
Projection Inequality (2026), Proposition 4.2:
  https://archive.ymsc.tsinghua.edu.cn/pacm_download/743/12781--2026.8.26.pdf
For a unit a perpendicular to 1 and S={u in Delta_9 : a.u=t}, with direction
F, their formula is
  vol_8(S)*vol_8(P_F[-1/2,1/2]^10)=D(a)*f_{a.U}(t)/9!,
where U is uniform in Delta_9. Set b=a-t*1. Writing X=T U, T=sum X_i,
the independent Gamma(10,1) variable T has E(1/T)=1/9. Hence
  f_Z(0)=f_{a.U}(t)/9,  D(b)=D(a).
The proved bound gives the target section-projection product <=9/8! for
these directions at every offset. Together with the arbitrary-polytope
section representation proved in the PDF, it bounds the corresponding
ten-facet bodies by the simplex ratio. Directions with at least three
coefficients of each sign are not covered by this certificate.

Analytic density recurrence: write the negative magnitudes as
0<a_1<=...<=a_k and positive magnitudes as 0<c_1<=...<=c_l, k+l=10.
Let L_ij=product_{u>=i,v>=j}(a_u+c_v). The density of the difference of
the remaining two exponential-phase chains, multiplied by L_ij, satisfies
  H_kl=1,
  H_ij=C_ij H_(i+1,j)+E_ij H_(i,j+1),
  C_ij=c_j product_{v>j}(a_i+c_v),
  E_ij=a_i product_{u>i}(a_u+c_j).
Off-grid terms are zero. Memorylessness gives the transition probabilities
c_j/(a_i+c_j) and a_i/(a_i+c_j); the last two phases have density
1/(a_k+c_l) at zero. Thus f_Z(0)=H_11/L_11. Ordered magnitudes give
  D=sum_i(l+2i-k-1)a_i+sum_j(k+2j-l-1)c_j.
The target is equivalent to N=9 L_11-D H_11 >=0, since L_11>0.

For k=1, independent ordered gaps within the two sign groups suffice.
For k=2, sort all ten absolute magnitudes and encode the sign order as a
word with two A's and eight C's. There are exactly choose(10,2)=45 such
words. If their successive nonnegative gaps are x_0,...,x_9, magnitude
number r is x_0+...+x_r. These cones cover every possible ordering;
equal levels are included. The checker reconstructs N in every cone.

Forty-three cones have nonnegative coefficients directly (including the
one-negative case). Three cones use the supplied exact certificates.
Their 1,479 blocks are monomial squares or rational weighted AM-GM
inequalities. A circuit with t*lower+upper=(t+1)*center and A,B,C>0 is
  A x^lower+B x^upper-C x^center >=0
whenever
  (A*(t+1)/t)^t * B*(t+1) >= C^(t+1).
The verifier checks this rational inequality, expands every block, and
checks that every remaining coefficient of 2N is nonnegative. Negative
coefficients in N alone are not counterexamples. A numerical optimizer
proposed some blocks; numerical feasibility and optimizer success are
not proof premises. The final replay imports no numerical optimizer.

Independent controls use the exponential partial-fraction formula. For
k=1 the density is product_j(a/(a+c_j))/a. For k=2 put
h(u)=product_j u/(u+c_j); the density is (h(a_2)-h(a_1))/(a_2-a_1),
or h'(a_1) when the means coincide. Every reconstructed polynomial is
cross-checked against this formula at exact rational inputs.

REPRODUCE (same pinned python-flint dependency as the local theorem)
  python -B check_low_sign_hyperplanes.py --check-report
  python -B -m unittest -v test_low_sign_hyperplanes.py
  python -B -O -m unittest -v test_low_sign_hyperplanes.py

Files:
  check_low_sign_hyperplanes.py         Complete exact checker; no optimizer.
  low-sign-hyperplane-certificates.json Three rational positivity certificates.
  low-sign-hyperplane-verification.json Coverage, counts and rational controls.
  test_low_sign_hyperplanes.py          Seven coverage and adversarial tests.

The replay checks 56,323,459 polynomial coefficients. Allow about a minute
and several gigabytes of memory, depending on hardware. There are 30
supplement-package tests after this extension. No claim is made for the
remaining sign cases, higher facet counts, or unrestricted minimality.
