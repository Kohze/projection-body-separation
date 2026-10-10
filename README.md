# Beyond point-generated product-join constructions for projection-body volume

Robin Gounder · Working research draft · 10 October 2026 · Version 1.3.1

[Read the paper](beyond-point-generated-projection-body-constructions.pdf) ·
[Versioned release](https://github.com/Kohze/projection-body-separation/releases/tag/v1.3.1) ·
[Citation metadata](CITATION.cff) · [Rights](RIGHTS.md)

This sixteen-page research note specifies a rational eighteen-dimensional simplex-section seed whose
iterated products and joins have projection-volume root limit strictly between
2.9280 and 2.9283. Together with an attributed prior upper theorem, it gives a
strict exponential separation from the entire class generated from a point
by products, joins and invertible affine equivalences. Explicit product-join recipes and a fixed 197-dimensional block give separation
in every dimension at least **9**. One explicit sequence simultaneously has
this finite separation and the stronger asymptotic limit.
An eight-dimensional seed gives an amplified rate between 2.8571 and 2.8573,
despite its initial ratio falling below the simplex ratio.

The simplex-section and two-upper-facet methods, operation calculus, recursion, tail method and class
upper theorem are prior work and are explicitly credited. Optimality and
global bibliographic priority are not claimed. This is an AI-assisted working
draft, not externally peer reviewed or proof-assistant formalized. The
manuscript includes an AI disclosure matching the companion papers and discusses the mathematical
and computational limits of the construction.

The final editorial audit separates the four seed families in the notation,
adds numbered comparison tables, and cites Yongxian Zhang under his public
author name. His newer positive sextic class bound is discussed as related
work; the proof retains the earlier replayed quadratic/quartic dependency.
The mathematical constants and all construction certificates are unchanged.
See [the current release audit](audit/final-release-review-v1.3.1.json).

## Reproduce

Python 3.11 or newer; standard library only. From the repository root:

```sh
python -B verify_delivery.py
python -B reproduction/verify_all.py --regenerate
python -B research/section-seeds/check_section_seed.py --check-report
python -B -m unittest discover -s research/section-seeds -p 'test_*.py' -v
python -B -O -m unittest discover -s research/section-seeds -p 'test_*.py' -v
python -B research/polygon-seeds/check_polygon_seed.py --check-report
python -B -m unittest discover -s research/polygon-seeds -p 'test_*.py' -v
python -B -O -m unittest discover -s research/polygon-seeds -p 'test_*.py' -v
```

The checks recompute complete rational seed geometry, compare the closed
formulas, verify the 224 block inequalities, reconstruct the rational recursion,
check infinite-tail hypotheses, replay the exact dimension-nine class frontier,
check 39 finite Bellman bounds and 197 explicit residue witnesses, and prove
the fixed-block extension in every larger dimension. The original 16 unit tests run
in normal and optimized Python. The principal section seed has an exact outward
interval certificate, complete basis and facet checks, two generic-ray checks,
and six additional tests. See [its proof and instructions](research/section-seeds/README.txt).
The simpler symmetric polygon seed retains its rational Laplace-transform
certificate and five tests, with a certified limit between 2.8900 and 2.8902.
See [the comparison seed](research/polygon-seeds/README.txt).
Certificate regeneration occurs in temporary files and leaves delivered files
unchanged. The own-construction checks need no network access.

The whole-class upper theorem is an essential external analytic dependency.
Its successful exact replay record is supplied. To fetch its byte-pinned
upstream package and replay its finite obligations:

```sh
python -B reproduction/verify_all.py --regenerate --with-prior
```

This optional command needs network access on first use. Finite replay does not
replace mathematical review of the imported analytic argument. Checkers were
developed within the same AI-assisted workflow; algorithmic independence does
not mean independent authorship. See [detailed instructions](reproduction/README.txt).

## Manuscript and data

`main.tex` is the editable paper source with its bibliography. To rebuild the
named PDF using pdflatex and the packages declared in that source:

```sh
python -B build_paper.py
```

The `reproduction/` folder is a sealed snapshot with matching manuscript
source/PDF, all exact data and programs, and `ARTIFACTS.sha256`. `audit/` contains
the source/dependency ledger, layout record, revision record and historical
internal reviewer scores. Historical review records describe their respective
editions and do not constitute external peer review. `paper-package-manifest.json`
records every file in this public edition except the manifest itself.
Rebuilding a PDF may change its metadata bytes; a rebuilt editable manuscript
does not silently alter the sealed reproduction snapshot.

Original Python code and generated certificate data are MIT licensed;
manuscript rights and third-party terms are recorded separately in [RIGHTS.md](RIGHTS.md).

## Dimension-nine certificate

`reproduction/threshold-recipes.json` specifies a 420-node operation graph and
one witness in each dimension 9 through 245. Numerical exploration selected
the recipes; search scores and optimizer success are not proof premises.
`produce_threshold.py` reconstructs exact states from the frozen recipes.
`check_threshold.py` independently checks those states against recomputed
seed geometry, bounds the finite class envelope by rational tangent estimates,
and proves the finite constants needed for all-dimensional propagation.

The original growth certificate still replays the older 15,500 fixed-block
and simplex-padding argument as a historical control. The current threshold
is **9**, proved in `threshold-verification.json` and Section 7 of the paper.
Nine is a sufficient dimension, not a proved minimum over all convex bodies.
The geometric family, dimension-nine simplex counterexample phenomenon,
operation identities, Pareto algorithm and mixed Bellman theorem are prior
work and explicitly attributed. The finite witness search is not exhaustive
and makes no optimality or global priority claim.

## Minimality research supplement

[Read the supplement](research/minimality/minimality.pdf) ·
[Exact checker and certificate](research/minimality/README.txt)

The supplement proves that nine is the first separation dimension within
the entire class generated from paired two-upper-facet seeds by products,
joins and affine maps. A short analytic proof and a separate exact polynomial
certificate establish the seed bound through dimension eight; an invariant
envelope proves closure under every operation tree. The checker
also cross-checks the point-generated class through dimension nine without
Pareto pruning. A further result rules out centred asymmetric two-facet cuts
with tilt range at most 1/500, with an explicit strict deficit. The unrestricted
problem is also formulated as a section--projection inequality for every
facet count. A general rational-polytope interface checks individual geometry
and that exact representation beyond the paired family. A computer-assisted
theorem also proves a nonpositive first derivative for every two-upper-facet
direction in dimension eight, without centring. Its four sign cases reduce to
17,265,590 positive integer coefficients. This is a local derivative theorem;
it does not bound arbitrary finite deformations. Thirty-five adversarial and
positive tests run in normal and optimized Python.

An additional executable research result bounds every offset hyperplane
section with ten coordinates when either side has at most two nonzero
coefficients. Its 46 cones are checked by reconstructing 56,323,459 integer
polynomial coefficients and verifying 1,479 rational certificate blocks.
The analytic reduction and exact certificates are documented in
[the research instructions](research/minimality/README.txt). This result
covers a family of ten-facet bodies; the full ten-facet bound remains open.
These additional research artifacts extend the results described in the PDF.

A further [analytic corollary](research/minimality/zonotope-local-extension.txt)
extends the local derivative bound to every translated zonotope support
deformation, with any finite number of hinge terms. Its loss adds exactly,
and the triangle inequality bounds the combined gain by the individual gains.
The argument imposes no facet-count bound within this family. It remains a
first-derivative result at a simplex; it gives neither a finite neighbourhood
bound nor the assertion for arbitrary support polytopes. A standard-library
checker includes exact repeated- and zero-coefficient controls.

**Global minimality remains unproved.** The supplement shows that proving
nine minimal over all convex bodies is equivalent to proving the unrestricted
simplex bound in dimension eight. General asymmetric seeds and arbitrary
convex bodies need not belong to the generated class. This research supplement is
separate from the main manuscript and its sealed reproduction snapshot;
its initial edition accompanied v1.1.0.

```sh
python -B research/minimality/check_minimality.py --check-report
python -B research/minimality/check_unrestricted.py --check-report
python -B research/minimality/check_zonotope_local.py --check-report
python -m pip install -r research/minimality/requirements-all-cuts.txt
python -B research/minimality/check_all_cuts.py --check-report
python -B research/minimality/check_low_sign_hyperplanes.py --check-report
python -B -m unittest discover -s research/minimality -p 'test_*.py' -v
python -B -O -m unittest discover -s research/minimality -p 'test_*.py' -v
```

The first three supplement checkers use only the standard library. The all-cut
polynomial proof and its eight tests require the optional pinned dependency
`python-flint==0.9.0`. The full polynomial check takes several minutes and can
use several gigabytes of memory. It reconstructs every coefficient from the
analytic recurrence rather than trusting a supplied list of coefficients.
