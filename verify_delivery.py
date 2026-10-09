"""Verify the versioned paper/data inventory without modifying delivered files."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise ValueError(message)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=json.loads((ROOT/'paper-package-manifest.json').read_text())
    required={'main.tex','beyond-point-generated-projection-body-constructions.pdf',
              'README.md','LICENSE','RIGHTS.md','CITATION.cff','verify_delivery.py',
              'reproduction/ARTIFACTS.sha256'}
    seen=set()
    for row in manifest['files']:
        name=row['path']
        path=(ROOT/name).resolve()
        require(path.is_relative_to(ROOT.resolve()),'Unsafe inventory path')
        require(name not in seen,'Duplicate inventory path')
        seen.add(name)
        require(path.is_file() and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],
                'Delivery mismatch: '+name)
    require(required<=seen,'Incomplete paper inventory')
    for a,b in [('main.tex','reproduction/beyond-point-generated.tex'),
                ('beyond-point-generated-projection-body-constructions.pdf','reproduction/beyond-point-generated.pdf')]:
        require(sha(ROOT/a)==sha(ROOT/b),'Manuscript/reproduction snapshot mismatch')
    print('PASS: public paper inventory ('+str(len(seen))+' files); source and PDF match the sealed reproduction snapshot.')

if __name__=='__main__':main()
