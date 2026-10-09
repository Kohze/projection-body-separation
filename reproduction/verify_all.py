"""Replay the new exact certificates and check their delivery hashes."""
from fractions import Fraction as F
import argparse
import hashlib
import json
from math import factorial
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
REQUIRED_ARTIFACTS = {
    'README.txt', 'beyond-point-generated.tex', 'beyond-point-generated.pdf',
    'build_seeds.py', 'produce_growth.py', 'exact_model.py', 'check_seeds.py',
    'check_growth.py', 'verify_all.py', 'test_certificate_checks.py',
    'seed-eight.json', 'seed-twelve.json', 'seed-geometry-verification.json',
    'growth-certificate.json', 'growth-verification.json', 'replay_prior.py',
    'prior-input-manifest.json', 'prior-mixed-upper-replay.json', 'source-audit.json',
    'build_blocks.py', 'check_block.py', 'block-197.json', 'block-197-verification.json',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(arguments):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable]+arguments, cwd=ROOT, text=True, capture_output=True, env=environment)
    require(result.returncode == 0, 'Command failed: '+str(arguments)+'\n'+result.stdout+result.stderr)
    return result.stdout+result.stderr


def manifest(allow_missing=False):
    path = ROOT/'ARTIFACTS.sha256'
    if not path.exists():
        require(allow_missing, 'Missing delivery manifest; --assembly is only for preparing an unsealed package')
        print('Assembly check: delivery manifest not yet sealed.', flush=True)
        return 0
    rows = path.read_text().splitlines()
    seen = set()
    for row in rows:
        expected, name = row.split('  ', 1)
        require(re.fullmatch('[0-9a-f]{64}', expected) is not None, 'Invalid SHA-256 encoding')
        require(name not in seen, 'Duplicate manifest entry: '+name)
        seen.add(name)
        require(Path(name).name == name and name not in ('.', '..'), 'Unsafe manifest path')
        require((ROOT/name).is_file() and digest(ROOT/name) == expected, 'Artifact mismatch: '+name)
    require(REQUIRED_ARTIFACTS <= seen, 'Manifest omits required proof/delivery files: '+str(sorted(REQUIRED_ARTIFACTS-seen)))
    print('PASS: delivery manifest ('+str(len(rows))+' files).', flush=True)
    return len(rows)


def main():
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regenerate', action='store_true')
    parser.add_argument('--assembly', action='store_true', help='Preparing a package before its delivery manifest is sealed')
    parser.add_argument('--with-prior', action='store_true', help='Network fetch and replay of the external upper theorem')
    args = parser.parse_args()
    count = manifest(args.assembly)
    with tempfile.TemporaryDirectory(prefix='projection-proof-check-') as directory:
        temporary = Path(directory)
        if args.regenerate:
            run(['build_seeds.py', '--output-directory', directory])
            run(['produce_growth.py', '--output-directory', directory])
            run(['build_blocks.py', '--output-directory', directory])
            generated = ('seed-eight.json', 'seed-twelve.json', 'growth-certificate.json', 'block-197.json')
            require(all(digest(ROOT/name) == digest(temporary/name) for name in generated), 'Producer regeneration changed certificate bytes')
            print('PASS: byte-identical certificate regeneration in temporary files.', flush=True)
        geometry = temporary/'geometry.json'
        run(['check_seeds.py', '--report', str(geometry)])
        require(digest(geometry) == digest(ROOT/'seed-geometry-verification.json'), 'Regenerated geometry report changed bytes')
        print('PASS: complete rational seed geometry and lifted minors.', flush=True)
        # Formula/geometry comparison is additional to both independent checkers.
        from exact_model import SEEDS, state
        for row in json.loads(geometry.read_text()):
            n, tilts, denominator = SEEDS[row['name']]
            s = state(n, [F(t, denominator) for t in tilts])
            for key in ('R', 'a', 'Q'):
                require(s[key] == F(*map(int, row[key])), 'Closed formula disagrees with geometry: '+key)
            require(s['I'] == factorial(n)*F(*map(int, row['polytope_volume'])), 'Volume formula disagrees with geometry')
        print('PASS: closed formulas agree with independent geometry.', flush=True)
        block_report = temporary/'block.json'
        run(['check_block.py', '--report', str(block_report)])
        require(digest(block_report)==digest(ROOT/'block-197-verification.json'), 'Regenerated block report changed bytes')
        print('PASS: explicit 224-facet description of the dimension-197 block.', flush=True)
        for mode in ([], ['-O']):
            report = temporary/('growth-optimized.json' if mode else 'growth.json')
            run(mode+['check_growth.py', '--self-test', '--geometry-report', str(geometry), '--report', str(report)])
            require(digest(report) == digest(ROOT/'growth-verification.json'), 'Regenerated growth report changed bytes')
        print('PASS: exact growth, analytic endpoint hypotheses, all 197 residues, finite separation; normal and optimized Python.', flush=True)
        print(run(['-m', 'unittest', '-v', 'test_certificate_checks.py']).strip(), flush=True)
        run(['-O', '-m', 'unittest', '-v', 'test_certificate_checks.py'])
        print('PASS: all ten unit tests also pass under optimized Python.', flush=True)
        if args.with_prior:
            report = temporary/'prior.json'
            print(run(['replay_prior.py', '--report', str(report)]).strip(), flush=True)
            require(digest(report) == digest(ROOT/'prior-mixed-upper-replay.json'), 'Prior replay differs from delivered record')
    prior = json.loads((ROOT/'prior-mixed-upper-replay.json').read_text())
    require(prior['status'] == 'PASS' and prior['mathematics_replayed'] is True, 'Missing prior upper replay record')
    manifest(args.assembly)
    print(json.dumps(dict(status='PASS', manifest_files=count, unit_tests=10,
                          seed_geometry='independently recomputed', growth='independently recomputed',
                          delivered_files_modified=False,
                          external_upper='replayed now' if args.with_prior else 'saved successful replay; use --with-prior to rerun'), indent=2), flush=True)


if __name__ == '__main__':
    main()
