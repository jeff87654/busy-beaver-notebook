"""final30b.py (true-order version of final30.py): H13c stage-30 B-form (from tdrive_h13c.log, after CLR d=2 n=X15) rendered with true-order
representatives (k1 << U4 << U5 << U14 << U16 << X15 << U17, exact classes mod 2520) and run literally with lsim
(state H, head at the right end) to the halt."""
import re, sys, lsimpy, random
H13 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RK0LC_1LK0LL_0LM0LA_0LJ---'
S = "2^(k1-12) 1 7 z4 0 z5 1 z3 0^3 z2 0 z2 0 10 0^3 (U5+1) 2^(4/21*U4-76/21) 1 7 6 0^3 [z4 2 z2 0 z2 0^4]^(1/9*U14-31/9) z4 2 z2 0^12 z2 (0 z5)^3 5 z4 [0 z5]^(1/3*U16-4/3) 0 z4 1^(X15) 0 (U17)"
from fractions import Fraction as F
def ev(e, v):
    e = e.strip('()')
    tot = F(0)
    for term in re.findall(r'[+-]?[^+-]+', e.replace(' ', '')):
        if '*' in term: c, a = term.split('*'); tot += F(c) * v[a]
        elif term.lstrip('+-') in v: tot += (-1 if term.startswith('-') else 1) * v[term.lstrip('+-')]
        else: tot += F(term)
    assert tot.denominator == 1, (e, tot); return int(tot)
def render(s, v):
    out = []
    toks = re.findall(r'\[[^\]]*\]\^\([^)]*\)|\([^)]*\)\^\d+|\S+\^\([^)]*\)|\S+', s)
    for t in toks:
        if t.startswith('['):
            inner, cnt = re.match(r'\[(.*)\]\^(\(.*\))', t).groups()
            out.append(render(inner, v) * ev(cnt, v)); continue
        m = re.match(r'\((.*)\)\^(\d+)$', t)
        if m: out.append(render(m.group(1), v) * int(m.group(2))); continue
        base, cnt = (t.split('^', 1) + ['1'])[:2] if '^' in t else (t, '1')
        c = ev(cnt, v)
        if base.startswith('z'): out.append('0' * int(base[1:]) * c); continue
        val = ev(base, v)
        out.append(('10' * val + '1') * c)
    return ''.join(out)
PHI = 40
def reps(seed, xres):
    """TRUE order (rank audit): k1 << P=U5 (iter 2 (U (w+11)) 4) << k2 (U4) << X15 << U16 = iter 3 (U X15) 4
    << U17 = iter 2 (U X15) 4 << U14 (huge-d round-end clear)"""
    rnd = random.Random(seed)
    v = {'k1': 1457 + 2520 * rnd.randint(1, 2)}
    v['U5'] = PHI + 2520 * rnd.randint(3, 4)
    v['U4'] = PHI + 2520 * rnd.randint(5, 6)
    v['X15'] = xres + 2520 * rnd.randint(8, 10)
    v['U16'] = PHI + 2520 * rnd.randint(13, 15)
    v['U17'] = PHI + 2520 * rnd.randint(18, 21)
    v['U14'] = PHI + 2520 * rnd.randint(30, 36)
    return v
for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6):
    xres = [0, 1, 2, 3, 4, 5][seed % 6] + 6 * 7
    v = reps(seed, xres)
    tape = render(S, v)
    x = lsimpy.run(H13, tape, kmode=0, maxs=10**12, head=len(tape), state='H')
    print(seed, {k: v[k] for k in v}, 'X15 mod 6 =', v['X15'] % 6, '->', x['line'][:60], flush=True)
