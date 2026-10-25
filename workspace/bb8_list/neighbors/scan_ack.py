"""Scan machines for Ackermann-style digit-list structure with kfit.py (neighbors_family_tools).

For each machine and each shape (state, suffix), kfit probes constructed configurations
K(ds; a; b) = 1^d1 0 ... 1^dn 0 1^a 0 1^b <suffix> [state>0] and fits count-down (R1), reset (R2) and
reset-with-trailing-zero-digits (R3) rules. A machine whose R1-R3 all fit behaves like a digit-list counter
that can handle lists of any length: the Ackermann-style structure of 1RB1RA_... Runs at Idle priority.

  stage1.exe PARENT machines.txt census.tsv 5000000   (shape census)
  python scan_ack.py census.tsv out.tsv
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / 'investigations' / 'neighbors_family_tools'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
SUFFIXES = ['01', '0', '1']


def fit(m, q, suf):
    try:
        r = subprocess.run([sys.executable, str(TOOLS / 'kfit.py'), m, '--shape', f'{q},{suf}', '--N', '1000000'],
                           cwd=TOOLS, capture_output=True, text=True, timeout=60, creationflags=LOW)
        out = r.stdout
    except subprocess.TimeoutExpired:
        return None
    line = next((l for l in out.splitlines() if l.strip().startswith('R1:')), '')
    parts = [p.strip() for p in line.split('|')]
    ok = lambda tag: any(p.startswith(tag) and 'no fit' not in p for p in parts)
    if ok('R1:') and ok('R2:') and ok('R3:'):
        return line.strip()
    return None


def scan(item):
    m, shapes = item
    hits = []
    for q, suf in shapes:
        h = fit(m, q, suf)
        if h:
            hits.append(f'{q},{suf}: {h}')
    return m, hits


def main():
    # input: stage1.exe output TSV (column 7 = shape census 'Q,suf:count;...'); probe the 4 most frequent shapes
    items = []
    for l in Path(sys.argv[1]).read_text().splitlines()[1:]:
        f = l.split('	')
        if len(f) < 7 or f[0].startswith('#') or f[6] == '-':
            continue
        cen = sorted(((int(c), qs) for qs, c in (x.rsplit(':', 1) for x in f[6].split(';'))), reverse=True)
        seen, shapes = set(), []
        for _, qs in cen:
            if qs not in seen:
                seen.add(qs); shapes.append(tuple(qs.split(',')))
        items.append((f[0], shapes[:4]))
    with ThreadPoolExecutor(max_workers=2) as pool, open(sys.argv[2], 'w', newline='\n') as out:
        for m, hits in pool.map(scan, items):
            out.write(f"{m}\t{len(hits)}\t{' || '.join(hits)}\n")
            out.flush()
            print(('DIGIT-LIST ' if hits else 'no         ') + m + ('   ' + hits[0][:120] if hits else ''), flush=True)


if __name__ == '__main__':
    main()
