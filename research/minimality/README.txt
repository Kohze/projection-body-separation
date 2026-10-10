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

REPRODUCE (Python 3.11 or newer; no network or third-party dependencies)
  python -B check_minimality.py --check-report
  python -B -m unittest -v test_minimality.py
  python -B -O -m unittest -v test_minimality.py

These commands do not modify delivered files. The optional --report PATH
flag writes the regenerated exact-arithmetic report to a path of your choice.
The checker reconstructs sparse polynomials from integer factors, proves
the cleared divided-difference identity, expands ordered gaps and checks
all 585 positive coefficients. It separately computes a supporting gradient
checks all 64 corner obligations for product closure of the finite envelope,
and enumerates unpruned product/join states through dimension 9. The
operation calculus is attributed prior work; the note supplies the analytic
reasoning that finite arithmetic alone cannot replace.

BUILD PDF (pdflatex and the packages declared in the source required)
  python -B build_note.py

The original paper's reproduction/verify_all.py also checks the dimension-nine
witness from its exact geometry. Those checks are separate from this
supplement's symbolic polynomial and supporting-gradient obligations.

RIGHTS
  Original checker code and certificate data use the repository's MIT license.
  Manuscript rights follow RIGHTS.md. Third-party inputs are linked and
  attributed, not redistributed. No global novelty or priority claim is made.
