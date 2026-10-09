# Beyond point-generated product-join constructions for projection-body volume

Robin Gounder · Working research draft · 9 October 2026 · Version 1.0.0

[Read the paper](beyond-point-generated-projection-body-constructions.pdf) ·
[Versioned release](https://github.com/Kohze/projection-body-separation/releases/tag/v1.0.0) ·
[Citation metadata](CITATION.cff) · [Rights](RIGHTS.md)

This eleven-page research note specifies a rational twelve-dimensional seed whose
iterated products and joins have projection-volume root limit strictly between
2.861 and 2.8611. Together with an attributed prior upper theorem, it gives a
strict exponential separation from the entire class generated from a point
by products, joins and invertible affine equivalences. A fixed 197-dimensional
block and simplex residues give separation in every dimension at least 15,500.
An eight-dimensional seed gives an amplified rate between 2.8571 and 2.8573,
despite its initial ratio falling below the simplex ratio.

The geometric family, operation calculus, recursion, tail method and class
upper theorem are prior work and are explicitly credited. Optimality and
global bibliographic priority are not claimed. This is an AI-assisted working
draft, not externally peer reviewed or proof-assistant formalized. The
manuscript includes a AI disclosure matching the companion papers and discusses the mathematical
and computational limits of the construction.

## Reproduce

Python 3.11 or newer; standard library only. From the repository root:

```sh
python -B verify_delivery.py
python -B reproduction/verify_all.py --regenerate
```

The checks recompute complete rational seed geometry, compare the closed
formulas, verify the 224 block inequalities, reconstruct the rational recursion,
check infinite-tail hypotheses, check all 197 residue bounds and the dimension
15,500 comparison, and run nine unit tests in normal and optimized Python.
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
