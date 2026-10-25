"""Probe the list-exhausted case of rebuilders at LARGE n (zero digits), where a rebuild-then-halt switch would act.

nob_screen.py grids n = 0..6.  A champion-start rebuilder first exhausts at n = 11 (it must rebuild there), and the
rebuilt list has about 12b digits, so the second exhaustion has a huge n.  A machine that rebuilds at n = 11 but
halts for some larger n (or for large n of some residue) is a rebuild-then-halt candidate, which in 9 states could
beat the BB(9) champion.

  python bign_probe.py WATCH_HITS.tsv OUT.tsv [WORKERS=4] [N=20000000]

For every NOBOUNDARY row: probe2.exe on K(0^n; 0; b) for n in NS and b in BS.  Output per machine: one letter per
(n, b) (H halt, K family configuration = rebuild, T neither within N steps), and a verdict:
  CANDIDATE  rebuilds at n = 11 for every b, but halts somewhere at larger n
  HALTS-AT-11  halts at the first exhaustion (champion-like)
  NO-HALT    no H anywhere
"""
from __future__ import annotations

import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent.parent / 'neighbors' / 'probe2.exe'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
NS = [11, 12, 13, 14, 15, 16, 17, 20, 23, 24, 25, 31, 32, 47, 48, 49]
BS = [0, 1, 2, 3, 4, 5, 8, 13]
TRX = re.compile(r'([LR]),([A-P]),P=([01-]*),u=([01]+),s=([01]+),d=(\d+)d\+(\d+),b=(\d+)b\+(\d+),S=([01-]*)$')


def probe(m, t, n_steps):
    g = TRX.match(t)
    if not g:
        return None
    o, q, P, u, s, al, be, alB, beB, S = g.groups()
    probes = [','.join(['0'] * n) + f';0;{b}' for n in NS for b in BS]
    r = subprocess.run([str(PROBE), m, o, q, P or '-', u, s, al, be, alB, beB, S or '-', str(n_steps), *probes],
                       capture_output=True, text=True, creationflags=LOW)
    out = []
    for line in r.stdout.splitlines():
        res = line.split('->', 1)[1] if '->' in line else ''
        out.append('H' if 'HALT' in res else 'T' if 'TIMEOUT' in res else 'K')
    if len(out) != len(probes):
        return None
    return [''.join(out[i * len(BS):(i + 1) * len(BS)]) for i in range(len(NS))]


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    n_steps = int(sys.argv[4]) if len(sys.argv) > 4 else 20_000_000
    rows = []
    for line in src.read_text().splitlines():
        f = line.split('\t')
        if len(f) >= 3 and f[0] == 'NOBOUNDARY':
            rows.append((f[1], f[2]))
    rows = list(dict(rows).items())

    def job(mt):
        m, t = mt
        g = probe(m, t, n_steps)
        if g is None:
            return m, t, 'NO-TEMPLATE', '-'
        at11 = g[0]
        later = ''.join(g[1:])
        if 'H' in at11:
            v = 'HALTS-AT-11'
        elif 'H' in later:
            v = 'CANDIDATE' if set(at11) == {'K'} else 'CANDIDATE?'
        else:
            v = 'NO-HALT'
        return m, t, v, ' '.join(f'n{n}:{s}' for n, s in zip(NS, g))

    with ThreadPoolExecutor(workers) as ex, dst.open('w') as f:
        f.write(f'machine\ttemplate\tverdict\tgrid (b = {BS})\n')
        for m, t, v, gs in ex.map(job, rows):
            f.write(f'{m}\t{t}\t{v}\t{gs}\n')
            f.flush()
            if v.startswith('CANDIDATE'):
                print(f'{v} {m} {gs}', flush=True)
    tally = {}
    for l in dst.read_text().splitlines()[1:]:
        v = l.split('\t')[2]
        tally[v] = tally.get(v, 0) + 1
    print(f'{len(rows)} NOBOUNDARY machines probed at large n: {tally}')


if __name__ == '__main__':
    main()
