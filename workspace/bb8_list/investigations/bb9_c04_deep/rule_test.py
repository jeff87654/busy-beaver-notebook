"""rule_test.py SEED N : randomized symbolic-rule test of the cascade exhaustion rule.
Random context  far..., [triples (6R+9|6R+12) and "s y" pairs], T_adj, 1^P, 0, 2, z2 | 1^k  (m=1, r=3R0+2, t), random P, t, R.
Predicted result of each exhaustion (until the chain enters L < 60):
  L0 = 3k-5; while L%5: emit s_r, y=(L+d_r)/5, L=(3L+c_r)/5.  Stop at L%5==0 (L>=60):
   s>=1: ... (T_adj-3) (6R+9) [s y]* 1^(P-7) 0 2 z2 X 1^k'      s=0: ... (T_adj-3) (6R+12) 1^(P-3) 0 2 z2 X 1^k'
  with X = (L-30)/5+8, k' = (L-30)/5, t' = t+3s; the CL then clears X 1^k' (pkf4 reports k=k') with the next R, and the next
  exhaustion starts from k'+1 zeros.  Compares pkf4's pre-jump view string and t, k exactly."""
import subprocess, sys, random, re
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
C = {1: 32, 2: -46, 3: -64, 4: -52}; D = {1: -21, 2: 3, 3: 7, 4: 11}; S = {1: ['4', '5'], 2: ['2'], 3: ['6'], 4: ['4']}
def rle(toks):
    out = []; i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]: j += 1
        out.append(toks[i] + ('*%d' % (j - i) if j - i > 1 else '')); i = j
    return ' '.join(out)
import os, json
A = json.loads(os.environ.get('PDEC_A', '{"1": 11, "2": 4, "3": 6, "4": 6}'))   # per-branch parked-list loss; base 3
def PDEC(branches): return 3 + sum(A[str(r)] for r in branches)
def predict(far, Tadj, P, k, t, Rs):
    """far: list of token strings (far->near) before Tadj.  Returns list of (view, t, k') per exhaustion, or stops when L0<60."""
    res = []; ctx = list(far); adj = Tadj; n = k; ri = 0
    R = Rs[0]
    while True:
        L = 3 * n - 5
        if L < 60: break
        toks = []; s = 0; branches = []
        while L % 5:
            r = L % 5; branches.append(r); toks += S[r] + [str((L + D[r]) // 5)]; L = (3 * L + C[r]) // 5; s += 1
            if L < 60: return res          # chain enters the window mid-exhaustion: stop predicting
        kp = (L - 25) // 5; X = kp + 7; t = t + 3 * (s + 1)
        if s >= 1:
            ctx = ctx + [str(adj - 3), str(6 * R + 9)] + toks[:-1]; adj = int(toks[-1]) + 3   # last token written carries +3
        else: ctx = ctx + [str(adj - 3)]; adj = 6 * R + 12
        P -= PDEC(branches)                                # parked-list loss: base 3 + per-branch a_r
        view = rle(ctx + [str(adj)] + ['1'] * P + ['0', '2', 'z2', str(X)] + ['1'] * kp)
        res.append((view, t, kp, tuple(branches))); n = kp; ri += 1
        if ri >= len(Rs): break
        R = Rs[ri]
    return res
def main():
    seed, N = int(sys.argv[1]), int(sys.argv[2]); rnd = random.Random(seed); ok = bad = skipped = 0; pexact = 0
    def mask(v): return re.sub(r'1\*(\d+) 0 2 z2', '1*? 0 2 z2', v)
    def pcount(v):
        m = re.search(r'1\*(\d+) 0 2 z2', v); return int(m.group(1)) if m else -1
    for case in range(N):
        far = ['0', '0'] + [str(rnd.randrange(30, 3000)) for _ in range(rnd.randrange(1, 4))]
        for _ in range(rnd.randrange(0, 4)):
            R = rnd.randrange(40, 2500); far.append(str(6 * R + rnd.choice([9, 12])))
            for _ in range(rnd.randrange(0, 3)): far += rnd.choice([['4', '5'], ['2'], ['6'], ['4']]) + [str(rnd.randrange(7, 2500))]
        Tadj = int(far.pop()) if len(far) > 2 and rnd.random() < 0.8 else rnd.randrange(7, 2500)
        if len(far) < 2: far = ['0', '0']
        P = rnd.randrange(600, 2500); t = rnd.randrange(18, 60); R0 = rnd.randrange(40, 300)
        Rs = sorted(rnd.randrange(60, 900) for _ in range(6))
        k = 3 * rnd.randrange(8, 700)
        pred = predict(far, Tadj, P, k, t, [R0] + Rs)
        if not pred: skipped += 1; continue
        kt = ','.join(far + [str(Tadj)]) + ',1*%d,0,2,z2,1*%d;1;%d;%d' % (P, k, 3 * R0 + 2, t)
        o = subprocess.run(['./pkf4.exe', M, '--kt', kt, '--Rlist', ','.join(map(str, Rs)), '--R', str(Rs[-1]), '--rmod', '36', '--exactcap', '1000',
                            '--jumps', str(len(pred)), '--view', '100000', '--maxs', '2e11', '--maxt', '2e11'], capture_output=True, text=True).stdout
        got = []
        for l in o.splitlines():
            if l.startswith('J'):
                h, v = l.split('|', 1); m = re.search(r't=(\d+) k=(\d+)', h); got.append((v.strip(), int(m.group(1)), int(m.group(2))))
        Pprev = P
        for i in range(min(len(got), len(pred))):
            pc = pcount(got[i][0]); print('PDEC', pred[i][3], Pprev - pc); Pprev = pc
        gm = [(mask(v), a, b) for v, a, b in got]; pm = [(mask(v), a, b) for v, a, b, br in pred]
        if gm == pm:
            ok += 1; full = got == [p[:3] for p in pred]; pexact += full
            print('case %d: ok (%d exhaustions), P exact: %s' % (case, len(pred), full), flush=True)
        else:
            bad += 1; print('MISMATCH case %d kt=%s' % (case, kt[:140]))
            for i in range(max(len(gm), len(pm))):
                g = gm[i] if i < len(gm) else None; p = pm[i] if i < len(pm) else None
                if g != p: print('  exh %d' % (i + 1)); print('   pred', str(p)[:300]); print('   got ', str(g)[:300]); break
            sys.stdout.flush()
    print('SUMMARY ok', ok, 'bad', bad, 'skipped', skipped, 'P-exact', pexact)
main()
