PROJECTION-BODY SEPARATION -- VERSION 1.0.0

This standalone folder contains the eleven-page manuscript, editable main.tex,
exact reproduction snapshot, source audit, internal review records and citation
metadata. README.md gives the current public-edition instructions.

Repository: https://github.com/Kohze/projection-body-separation
Release: https://github.com/Kohze/projection-body-separation/releases/tag/v1.0.0

Build: python -B build_paper.py
Verify delivery: python -B verify_delivery.py
Reproduce: python -B reproduction/verify_all.py --regenerate
Replay attributed external upper theorem (first use requires network):
  python -B reproduction/verify_all.py --regenerate --with-prior

The discussion, conclusion and disclosure/availability sections are included.
The exact mathematical constants and certificates are unchanged from the
preceding reviewed draft. It remains a working draft without external peer
review or a proof-assistant formalization. Original code/data use MIT terms;
manuscript and third-party rights are recorded in RIGHTS.md.
