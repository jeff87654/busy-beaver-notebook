"""Size-ordering robustness of every recorded stage (ghf8.py --dump), gh0LH verifier.
The follower gives huge symbols small representatives in arbitrary relative order. A stage whose outcome depends on
WHICH huge value is bigger (or on a huge value against an exact one, e.g. 98298) would be mis-followed.
For each recorded stage with huge symbols, we re-run it under several size orderings:
  * every huge representative exceeds 2 * (largest exact token or count in the window) + 2520
    (real huge values are > 2^60 > every exact value);
  * orderings: follower order, reversed, accumulator (rightmost symbol) smallest, accumulator largest, 2 random;
    successive symbols in an ordering are separated by a factor ~3 (rep_k = residue rep + 2520 * j_k, j_k = base*3^rank).
The literal output (ksim6.exe) must equal the follower's affine forms evaluated at the new representatives.
Budget exhaustion is reported separately (not a pass, not a structural failure).
  python order_check.py DUMP.jsonl [--maxsteps N] [--seed S] [--sample N]"""
import sys, json, random, subprocess, argparse, itertools
from fractions import Fraction
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
IDLE = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
def D(m): return '0' * (-m) if m < 0 else '10' * m + '1'
def m2(s, k):
    s = Fraction(s); return (s.numerator * pow(s.denominator, -1, 2 ** k)) % 2 ** k
def runs_of(vals):
    out = []
    for v in vals:
        if out and out[-1][0] == v: out[-1][1] += 1
        else: out.append([v, 1])
    return out
def merge(rr):
    out = []
    for v, c in rr:
        if out and out[-1][0] == v: out[-1] = [v, out[-1][1] + c]
        else: out.append([v, c])
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dump'); ap.add_argument('--maxsteps', type=int, default=3 * 10 ** 10)
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--sample', type=int, default=0); ap.add_argument('--only', default='')
    a = ap.parse_args(); random.seed(a.seed)
    sv = subprocess.Popen(['./ksim6.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, creationflags=IDLE)
    recs = [json.loads(l) for l in open(a.dump)]
    idx = [i for i, r in enumerate(recs) if r['syms']]
    if a.sample and a.sample < len(idx): idx = sorted(random.sample(idx, a.sample))
    if a.only: idx = [int(x) for x in a.only.split(',')]
    n = bad = nto = 0; multi = 0; badlist = []
    for i in idx:
        rec = recs[i]; win = rec['win']; syms = rec['syms']; k = len(syms)
        exact = [0]
        for it in win:
            if it[0] == 'R':
                for x in (it[1], it[2]):
                    if not isinstance(x, dict): exact.append(abs(x))
            else:
                for v, c in it[1]:
                    if not isinstance(v, dict): exact.append(abs(v))
                if not isinstance(it[2], dict): exact.append(it[2])
        base_j = (2 * max(exact)) // 2520 + 1
        r0 = []
        for x in syms:
            r2 = m2(x['s2'], 3); ro = x['odd'] % 315
            r0.append(r2 + 8 * (((ro - r2) * pow(8, -1, 315)) % 315))
        orders = [list(range(k)), list(range(k))[::-1]]
        if k > 1:
            orders.append([0] + list(range(1, k)))             # symbol 0 (the accumulator) smallest
            orders.append(list(range(1, k)) + [0])             # symbol 0 largest
            for _ in range(2): p = list(range(k)); random.shuffle(p); orders.append(p)
            multi += 1
        seen = set()
        for order in orders:            # order[rank] = symbol index
            if tuple(order) in seen: continue
            seen.add(tuple(order))
            reps = [0] * k
            for rank, s in enumerate(order): reps[s] = r0[s] + 2520 * (base_j * 3 ** rank)
            def val(x):
                if isinstance(x, dict): return reps[next(j for j, y in enumerate(syms) if y == x)]
                return x
            parts = []
            for it in win:
                if it[0] == 'R': parts.append(D(val(it[1])) * val(it[2]))
                else: parts.append(''.join(D(val(v)) * c for v, c in it[1]) * val(it[2]))
            w = ''.join(parts) + '10101010'
            sv.stdin.write(f'{w} {len(w)} G {a.maxsteps}\n'); sv.stdin.flush()
            o = sv.stdout.readline().split()
            n += 1
            if o and o[0] == 'T': nto += 1; print(f'#{i} order {order}: over budget (max rep {max(reps)})', flush=True); continue
            if o and o[0] == 'K' and '@' in o: o = o[:o.index('@')]
            if not o or o[0] != 'K':
                bad += 1; badlist.append(i); print(f'#{i} order {order}: no K-moment: {o[:5]}', flush=True); continue
            got = merge(runs_of([int(x) for x in o[3:]]))
            exp = []
            for vf, cf in rec['out']:
                def ev(f):
                    v = Fraction(f['const']) + sum(Fraction(c) * reps[int(kk)] for kk, c in f['coef'].items())
                    return int(v) if v.denominator == 1 else None
                exp.append([ev(vf), ev(cf)])
            if got != merge(exp):
                bad += 1; badlist.append(i)
                print(f'#{i} order {order} reps {reps}: MISMATCH\n   exp {merge(exp)[-10:]}\n   got {got[-10:]}', flush=True)
    print(f'{len(idx)} stages with huge symbols ({multi} with 2+), {n} ordered runs, {bad} failures, {nto} over budget; failing stages {sorted(set(badlist))[:30]}', flush=True)
if __name__ == '__main__':
    main()
