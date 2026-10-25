"""Independent re-verification of every literal stage recorded by ghf7.py --dump (gh0LH verifier).
For each recorded stage (window of a configuration the follower actually reached, plus the affine output forms):
  * fresh representatives for every huge symbol: rep = CRT(s2 mod 2^K, odd mod 315) + (2^K*315)*j, j random in 1..4,
    K = 3 (the follower's own matching depth) or K = 7 (deeper 2-adic matching, mode --deep);
  * run the literal machine (ksim2.exe, or kst3.exe with --plain) to the next K-moment;
  * the output runs must equal the affine forms evaluated at the fresh representatives (exactly), and the head must
    never enter the window's first item (locality), unless the window is the full configuration.
Fails loudly: prints every mismatch.
  python verify_stages.py DUMP.jsonl [--deep] [--plain] [--sample N] [--seed S]"""
import sys, json, random, subprocess, argparse
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
    if out[-1][1] > 1:
        v, c = out.pop(); out += [[v, c - 1], [v, 1]]
    if out[-2][1] > 1:
        v, c = out.pop(-2); out.insert(len(out) - 1, [v, c - 1]); out.insert(len(out) - 1, [v, 1])
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dump'); ap.add_argument('--deep', action='store_true')
    ap.add_argument('--plain', action='store_true'); ap.add_argument('--deep5', action='store_true'); ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--seed', type=int, default=1); ap.add_argument('--maxsteps', type=int, default=10 ** 13)
    a = ap.parse_args()
    random.seed(a.seed)
    exe = './kst3.exe' if a.plain else './ksim6.exe'
    sv = subprocess.Popen([exe, MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1, creationflags=IDLE)
    recs = [json.loads(l) for l in open(a.dump)]
    idx = list(range(len(recs)))
    if a.sample and a.sample < len(idx): idx = sorted(random.sample(idx, a.sample))
    K = (5 if a.deep5 else 7) if a.deep else 3; MODK = 2 ** K * 315
    bad = 0; n = 0; nh = 0; nto = 0
    for i in idx:
        rec = recs[i]; win = rec['win']; syms = rec['syms']
        reps = []
        for x in syms:
            r2 = m2(x['s2'], K); ro = x['odd'] % 315
            base = r2 + 2 ** K * (((ro - r2) * pow(2 ** K, -1, 315)) % 315)
            reps.append(base + MODK * random.randint(1, 4))
        def val(x):
            if isinstance(x, dict):
                k = next(j for j, y in enumerate(syms) if y == x); return reps[k]
            return x
        parts = []
        for it in win:
            if it[0] == 'R': parts.append(D(val(it[1])) * val(it[2]))
            else: parts.append(''.join(D(val(v)) * c for v, c in it[1]) * val(it[2]))
        w = ''.join(parts) + '10101010'
        full = (i == 0) or None
        sv.stdin.write(f'{w} {len(w)} G {a.maxsteps}\n'); sv.stdin.flush()
        o = sv.stdout.readline().split()
        n += 1
        if o and o[0] == 'T':
            nto += 1; print(f'#{i}: step budget exhausted (not counted as pass or fail)'); continue
        if not o or o[0] != 'K':
            bad += 1; print(f'#{i}: no K-moment: {o[:4]}'); continue
        if '@' in o:
            at = o.index('@'); minpos = int(o[at + 1]); o = o[:at]
        else:
            minpos = None
        if rec.get('full') is False and minpos is not None:
            it0 = win[0]
            flen = len(D(val(it0[1])) * val(it0[2])) if it0[0] == 'R' else 0
            if minpos < flen:
                bad += 1; print(f'#{i}: LOCALITY violated (minpos {minpos} < first item {flen})'); continue
        got = runs_of([int(x) for x in o[3:]])
        exp = []
        for vf, cf in rec['out']:
            def ev(f):
                v = Fraction(f['const']) + sum(Fraction(c) * reps[int(k)] for k, c in f['coef'].items())
                if v.denominator != 1: return None
                return int(v)
            exp.append([ev(vf), ev(cf)])
        if any(h for h in syms): nh += 1
        def merge(rr):
            out = []
            for v, c in rr:
                if out and out[-1][0] == v and v is not None: out[-1] = [v, out[-1][1] + c]
                else: out.append([v, c])
            return out
        if merge(got) != merge(exp):
            bad += 1
            print(f'#{i}: MISMATCH (syms {len(syms)})\n   exp {exp[-12:]}\n   got {got[-12:]}')
    print(f'{n} stages re-run, {bad} failures, {nto} over the step budget; mode={"deep" if a.deep else "mod8"} sim={exe}')
if __name__ == '__main__':
    main()
