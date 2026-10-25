"""Parameter-grid literal checks of the recorded stages (ghf8.py --dump) of the gh0LH verifier.
For every recorded stage window and every run with count >= MINC (a zero list, the D9 region, a block group ...),
the count is varied over a grid c + d (d in DELTAS); every huge symbol gets a fresh representative in its residue
class (CRT(s2 mod 8, odd mod 315) + 2520 j).  The literal outputs (next K-moment, ksim6.exe) must have the same run
structure and every token value / run count must be affine in d (equal second differences = 0).  Fails loudly.
  python grid_check.py DUMP.jsonl [--sample N] [--seed S]"""
import sys, json, random, subprocess, argparse
from fractions import Fraction
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
MINC = 10
DELTAS = [0, 3, 6, 9, 30]
def D(m): return '0' * (-m) if m < 0 else '10' * m + '1'
def m2(s, k):
    s = Fraction(s); return (s.numerator * pow(s.denominator, -1, 2 ** k)) % 2 ** k
def runs_of(vals):
    out = []
    for v in vals:
        if out and out[-1][0] == v: out[-1][1] += 1
        else: out.append([v, 1])
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dump'); ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args(); random.seed(a.seed)
    sv = subprocess.Popen(['./ksim6.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, creationflags=IDLE)
    recs = [json.loads(l) for l in open(a.dump)]
    idx = list(range(len(recs)))
    if a.sample and a.sample < len(idx): idx = sorted(random.sample(idx, a.sample))
    nchk = bad = 0
    for i in idx:
        rec = recs[i]; win = rec['win']; syms = rec['syms']
        reps = []
        for x in syms:
            r2 = m2(x['s2'], 3); ro = x['odd'] % 315
            reps.append(r2 + 8 * (((ro - r2) * pow(8, -1, 315)) % 315) + 2520 * random.randint(1, 3))
        def val(x):
            if isinstance(x, dict): return reps[next(j for j, y in enumerate(syms) if y == x)]
            return x
        cands = [p for p, it in enumerate(win) if it[0] == 'R' and val(it[2]) >= MINC and p < len(win) - 2]
        for p in cands:
            outs = []
            for d in DELTAS:
                parts = []
                for q, it in enumerate(win):
                    c = val(it[2]) + (d if q == p else 0)
                    if it[0] == 'R': parts.append(D(val(it[1])) * c)
                    else: parts.append(''.join(D(val(v)) * n for v, n in it[1]) * c)
                w = ''.join(parts) + '10101010'
                sv.stdin.write(f'{w} {len(w)} G 10000000000000\n'); sv.stdin.flush()
                o = sv.stdout.readline().split()
                if o and o[0] == 'K' and '@' in o: o = o[:o.index('@')]
                outs.append(o)
            nchk += 1
            if any(o[0] != outs[0][0] for o in outs):
                bad += 1; print(f'#{i} run {p}: outcome kind varies with the count: {[o[:3] for o in outs]}'); continue
            if outs[0][0] == 'H':
                if any(o[2:4] != outs[0][2:4] for o in outs): bad += 1; print(f'#{i} run {p}: halting state varies')
                continue
            rr = [runs_of([int(x) for x in o[3:]]) for o in outs]
            if any(len(r) != len(rr[0]) for r in rr):
                bad += 1; print(f'#{i} run {p}: run structure varies with the count: {[len(r) for r in rr]}'); continue
            for k in range(len(rr[0])):
                for f in (0, 1):
                    ys = [r[k][f] for r in rr]
                    sl = [Fraction(ys[j] - ys[0], DELTAS[j]) for j in range(1, len(DELTAS))]
                    if any(s != sl[0] for s in sl):
                        bad += 1; print(f'#{i} run {p}: output {k}.{f} not affine in the count: {ys}'); break
    print(f'{len(idx)} stages, {nchk} count-grids (deltas {DELTAS}), {bad} failures')
if __name__ == '__main__':
    main()
