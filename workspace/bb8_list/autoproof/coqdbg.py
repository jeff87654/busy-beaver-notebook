"""Debug helper: print Coq's goal just before the tactic at LINE:COL of a generated proof.

  python coqdbg.py FILE.v LINE COL
"""
import subprocess
import sys
from pathlib import Path

COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'


def main():
    path, line, col = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    lines = path.read_text().split('\n')
    head = lines[:line - 1]
    cut = lines[line - 1][:col]
    dbg = cut + ' match goal with |- ?g => idtac "GOAL:" g end. Abort.'
    out = head + [dbg]
    tmp = path.with_name('AutoDbg.v')
    tmp.write_text('\n'.join(out) + '\n', newline='\n')
    r = subprocess.run([COQC, '-Q', r'..\..\third_party\busycoq\verify', 'BusyCoq', '-Q', '.', 'BB8', tmp.name],
                       capture_output=True, text=True, cwd=path.parent)
    txt = r.stdout + r.stderr
    i = txt.find('GOAL:')
    print(txt[i:i + 3000] if i >= 0 else txt[-3000:])
    for ext in ('.v', '.vo', '.glob', '.vok', '.vos'):
        p = tmp.with_suffix(ext)
        if p.exists():
            p.unlink()
    aux = tmp.with_name('.AutoDbg.aux')
    if aux.exists():
        aux.unlink()


if __name__ == '__main__':
    main()
