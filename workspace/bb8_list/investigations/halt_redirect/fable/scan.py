"""Outcome scan over constructed start structures.  usage: python scan.py FAMILY ustart uend [step] [--stages N]
FAMILY R1: [9^u 11 1^(2u+36) | a=1 | r=2]  (round-1 structure, stage-0 K-moment)
FAMILY R2: [227 9^u 8 3 1 0 0 9 1^(2u+1) | a=1 | r=1]  (round-2 rebuild structure)"""
import sys, argparse, io, contextlib
sys.path.insert(0, '.')
import gh_run
ap = argparse.ArgumentParser(); ap.add_argument('fam'); ap.add_argument('u0', type=int); ap.add_argument('u1', type=int)
ap.add_argument('--step', type=int, default=1); ap.add_argument('--stages', type=int, default=3000); ap.add_argument('--out', default=None)
a = ap.parse_args()
out = open(a.out, 'a') if a.out else sys.stdout
for u in range(a.u0, a.u1 + 1, a.step):
    if a.fam == 'R1':
        start = [9] * u + [11] + [1] * (2 * u + 36) + [1, 2]
    else:
        start = [227] + [9] * u + [8, 3, 1, 0, 0, 9] + [1] * (2 * u + 1) + [1, 1]
    lines = []
    res = gh_run.follow(0, 'std', a.stages, 200_000_000, log=lines.append, start=start)
    # endgame summary: the last 4 K lines (short form)
    ks = [l for l in lines if ' K: ' in l]
    reb = [l.split(' K: ')[0] for l in ks if ' 9^' in l.split(' K: ')[1].split('|')[0] and l.split(' K: ')[1].split()[0] not in ('9',) and not l.split(' K: ')[1].startswith('9')]
    tail = ' ;; '.join(l[:70] for l in ks[-3:])
    print(f'{a.fam} u={u} m={2*u+36 if a.fam=="R1" else 2*u+1} -> {res} stages={len(ks)} rebuilds_at={reb[:4]} | {tail}', file=out, flush=True)
