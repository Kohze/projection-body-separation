"""Fetch byte-pinned prior upper-bound inputs, then replay their own checker.

Without --directory, fetches to .prior-cache (network required once).
This is a replay of an attributed external theorem, not a new upper proof.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path)
    parser.add_argument('--report', type=Path, default=ROOT/'prior-mixed-upper-replay.json')
    args = parser.parse_args()
    target = (args.directory or ROOT/'.prior-cache').resolve()
    target.mkdir(parents=True, exist_ok=True)
    source = json.loads((ROOT/'prior-input-manifest.json').read_text())

    def fetch(row):
        name = Path(row['path']).name
        require(name not in ('', '.', '..') and '/' not in name and '\\' not in name, 'Invalid filename')
        path = target/name
        if not path.exists():
            require(args.directory is None, 'Missing supplied prior file: '+name)
            data = urllib.request.urlopen(row['url'], timeout=45).read()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'Downloaded hash mismatch: '+name)
            path.write_bytes(data)
        data = path.read_bytes()
        require(len(data) == row['bytes'], 'Prior size mismatch: '+name)
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'Prior hash mismatch: '+name)
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'], 'Git blob mismatch: '+name)
        return name

    with ThreadPoolExecutor(max_workers=6) as pool:
        names = list(pool.map(fetch, source['files']))
    print('Verified pinned prior files:', len(names), flush=True)
    subprocess.run([sys.executable, str(target/'verify.py'), '--mode', 'ordinary', '--report', str(args.report.resolve())],
                   cwd=target, check=True)


if __name__ == '__main__':
    main()
