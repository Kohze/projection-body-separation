# Changes

## 1.3.1 - 10 October 2026

Final editorial and release audit. Distinguish the generic recursion X_j,
the principal eighteen-dimensional sequence G_j, and the twelve-dimensional
sequence K_j used for the 197-dimensional block. Avoid reusing the latter
seed's state symbols for the eight-dimensional comparison. Add a seed summary
and numbered, captioned endpoint and finite-margin tables. Prevent floats
from interrupting sentences and set reproduction commands as a code block.
Condense repeated verification and discussion material while retaining the
proof obligations. Add PDF keywords and consistent edition metadata.

Cite the public author name Yongxian Zhang for the mxym repository sources
while retaining immutable proof pins. Cite the newer sextic envelope as
related work; the essential upper-bound dependency and certified constants
are unchanged. Update the citation ledger, internal reviewer scores,
source/dependency ledger and matching reproduction snapshots. Nineteen
references are cited. Unrestricted minimality and global optimality remain
unproved; no bibliographic-priority or external peer-review claim is made.

## 1.3.0 - 10 October 2026

Raise the certified amplified lower rate again, from 2.890 to 2.928, by
an explicit rational eighteen-dimensional simplex section with twenty-three
facets. Retain the nonuniform facet weights in the classical section/spline
calculation. Prove the density and gradient identities, regularity, genuine
facet hypotheses, and the interpolation identity used by the certificate.
Use outward integer arithmetic to enclose the seed state and prove
2.9280 < beta < 2.9283. Add a standard-library checker and six tests, all
passing in normal and optimized Python on Windows and Linux. Keep the
simpler polygon seed as a comparison. Update the sixteen-page manuscript,
integer-coordinate appendix, discussion, conclusion and reproduction metadata;
shorten the classical truncation appendix to its formula and primary sources.
The finite separation from dimension nine is retained. Global optimality,
unrestricted minimality and bibliographic priority remain unproved.

## 1.2.0 - 10 October 2026

Strengthen the main certified amplified lower rate from 2.861 to 2.890.
Specify a rational 15-dimensional simplex section with 18 facets by three
six-element orbits of integer planar vectors. Prove its exact seed state
using antipodal permutation symmetry, complementary minors, coarea and
a finite Laplace-transform identity. A separate standard-library checker
verifies every coefficient of that identity, three generic rays, the exact
state and infinite-tail endpoint arithmetic; five additional tests pass
in normal and optimized Python. Update the fifteen-page manuscript,
discussion, conclusion, citation metadata and reproduction instructions.
The original finite separation from dimension nine is retained. Global
minimality, seed/schedule optimality and bibliographic priority remain
unproved. All underlying classical methods and imported calculus remain
attributed; the contribution is the specified seed and stronger bound.

## Unreleased research supplement: dimension-nine minimality

Add a separate research supplement with an exact reduction of
global minimality to the unrestricted eight-dimensional simplex bound.
Prove that dimension nine is minimal within the entire class generated
from paired two-upper-facet seeds by products, joins and affine maps.
Supply an analytic proof, an independent 585-term positive-polynomial
certificate, all 64 exact product-closure corner checks, unpruned operation
states through dimension nine, and seven positive/adversarial tests.
Global minimality over arbitrary convex bodies remains unproved. The
v1.1.0 tag and release assets are unchanged. Its paper/reproduction snapshot
was unchanged during these supplement updates; v1.2.0 subsequently updates
the manuscript and adds the stronger polygon seed. CI also checks the supplement.

Extend the supplement with an equivalent unrestricted section--projection
inequality for every facet count, a strict finite neighbourhood bound for
centred asymmetric two-facet cuts, and a general exact rational-polytope
interface. Six geometric controls check the section identity, including an
eight-dimensional eleven-facet example and an asymmetric control at the
proved neighbourhood boundary. Add eight tests (15 supplement tests total),
and cite recent simplex slicing and stability work with its precise scope.
These additions do not prove the remaining universal inequality.

Remove the centring assumption for the first-derivative assertion at a
simplex. An exact computer-assisted proof covers all four mixed-sign cases
in dimension eight by checking 17,265,590 positive integer coefficients.
Provide the analytic exponential-race recurrence, reconstructing checker,
pinned optional python-flint dependency, rational cross-checks and eight
tests (23 supplement tests total). This local theorem does not prove the
finite all-cut inequality or global minimality.

## 1.1.0 - 10 October 2026

Prove separation from the entire point-generated class in every dimension
n >= 9, replacing the earlier sufficient threshold 15,500. Retain the
invariant dependence in the imported Bellman envelope; prove a uniform
finite class bound; add exact geometry for two rational seeds and a
420-node operation certificate covering 40 small dimensions and 197 residue
bases, followed by a rigorous infinite fixed-block extension. One exact
selection sequence also retains the certified asymptotic rate. Add six
adversarial/regression tests (16 total), attribute the prior Pareto algorithm,
and update the thirteen-page manuscript and its 17 references. Nine is
sufficient; minimality and global priority remain unclaimed.

## 1.0.1 - 9 October 2026

The optional external replay passed all mathematics on Linux, then encountered
a comparison failure caused solely by Windows CRLF versus Linux LF report
newlines. Normalize the wrapper's report bytes and supplied report to LF;
retain strict full-report hash comparison. Add a regression test covering
newline normalization, idempotence and preserved JSON values. There are now
ten unit tests. Update the manuscript and availability links to this patch.
No mathematical constants, geometry, recurrence certificate or prior inputs
change. The original v1.0.0 tag and assets remain available.

## 1.0.0 - 9 October 2026

Initial public manuscript, data and code edition with the discussion,
conclusion, requested companion-paper AI disclosure and 16 references.
