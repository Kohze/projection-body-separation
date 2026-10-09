"""Build this standalone paper without changing its reproduction snapshot."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

root=Path(__file__).resolve().parent
if not shutil.which('pdflatex'):
    raise SystemExit('Required executable missing: pdflatex')
with tempfile.TemporaryDirectory(prefix='projection-paper-build-') as directory:
    target=Path(directory)
    command=['pdflatex','-interaction=nonstopmode','-halt-on-error',
             '-file-line-error','-output-directory='+target.as_posix(),'main.tex']
    for _ in range(3):
        result=subprocess.run(command,cwd=root,capture_output=True,text=True,
                              encoding='utf-8',errors='replace')
        if result.returncode:
            raise RuntimeError((result.stdout+result.stderr)[-5000:])
    log=(target/'main.log').read_text(encoding='utf-8',errors='replace')
    issues=re.findall(r'(?:Overfull[^\n]*|Underfull[^\n]*|[^\n]*Warning[^\n]*)',log)
    if issues:raise RuntimeError('Unresolved build issues: '+str(issues))
    output=root/'beyond-point-generated-projection-body-constructions.pdf'
    shutil.copyfile(target/'main.pdf',output)
    print('Built '+str(output))
