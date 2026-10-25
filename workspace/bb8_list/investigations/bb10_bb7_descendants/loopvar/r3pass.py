"""Radius-3 fast scan with de-duplication (Idle).  python r3pass.py MACHINES OUTPREFIX FAMILY [CHUNKS]
pass 1: the real first-exhaustion cell only, with a configuration fingerprint at the cap;
pass 2: all cells of FAMILY (C28 or C2932) for one representative per (outcome, fingerprint) class that does not halt
at the first exhaustion.  Writes OUTPREFIX_p1.tsv, OUTPREFIX_p2.tsv."""
import subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
ms = Path(sys.argv[1]).read_text().split(); pre = sys.argv[2]; fam = sys.argv[3]
k = int(sys.argv[4]) if len(sys.argv) > 4 else 6
cells = (['tmpw/cs_e0r.txt'] + [f'tmpw/cs_c{n}.txt' for n in range(12, 20)]) if fam == 'C28' else \
        (H / 'tmpw' / 'cs4r_list.txt').read_text().split()
def run(machines, cellset, tag):
    ps = []
    for i in range(k):
        part = H / 'tmpw' / f'{tag}_in{i}.txt'; part.write_text('\n'.join(machines[i::k]) + '\n')
        ps.append(subprocess.Popen([str(H / 'cellscan.exe'), str(part), 'B', *cellset], cwd=H,
                                   stdout=open(H / 'tmpw' / f'{tag}_out{i}.txt', 'w'), creationflags=subprocess.IDLE_PRIORITY_CLASS))
    for p in ps: p.wait()
    return ''.join((H / 'tmpw' / f'{tag}_out{i}.txt').read_text() for i in range(k))
p1 = run(ms, cells[:1], pre + '_p1')
(H / f'{pre}_p1.tsv').write_text(p1)
reps = {}
for l in p1.splitlines():
    m, let, st, hs = l.split('\t')
    if let[0] != 'H':
        reps.setdefault(hs, m)
p2 = run(list(reps.values()), cells, pre + '_p2')
(H / f'{pre}_p2.tsv').write_text(p2)
print(len(ms), 'machines;', len(reps), 'classes not halting at E0')
