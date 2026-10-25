"""fam1.py: validate the v-coded rule set of the r/s/h/u family (all four 7-state machines share it) against literal runs.
v-coding: tape = 1^v1 0 ... 1^vn 0 1^A 0 1^B S (K-moment: head right of it in the template state, B fixed).
 D  [..,v+1;A] -> [..,v;3A+3]
 Bk [..,y+1,0^k;A] -> [..,y,3A+3-2k,2^(k-1);2]
 E  [0^k;A]: A odd HALT; A even -> [4,2^(3A/2-1);2]      (leading zeros are invisible)
Invariant Phi = A + sum(v) mod 2."""
import idle, sys, random
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short
FAM = [('1RB0LG_1RC1RB_0RD0RB_0LE1RD_0LD1LF_---1LA_1LC1LG', 'R,E,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', 6),
       ('1RB0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG', 'R,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0110', 2),
       ('1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1RA0LG_1LB1LG', 'R,A,P=-,u=1,s=0,d=1d+0,b=1b+0,S=1', 3),
       ('1RB1RE_1RC1RB_0LD0LG_0RA1LD_---1RF_1LG0RB_1LC1LG', 'L,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', 2)]
def strip(ds):
    i = 0
    while i < len(ds) and ds[i] == 0: i += 1
    return ds[i:]
def pred(ds, A):
    ds = strip(ds)
    if not ds or all(x == 0 for x in ds):
        return 'HALT' if A % 2 else ([4] + [2] * (3 * A // 2 - 1), 2)
    if ds[-1] > 0: return (strip(ds[:-1] + [ds[-1] - 1]), 3 * A + 3)
    k = 0
    while ds[-1 - k] == 0: k += 1
    y = ds[-1 - k]
    return (strip(ds[:-1 - k] + [y - 1, 3 * A + 3 - 2 * k] + [2] * (k - 1)), 2)
def literal(M, T, B, ds, A, steps=2 * 10**7):
    ev = kl.run(M, ds, A, B, steps, 0, 100000, T=T, pall=1)
    for e in ev[1:]:
        if e[0] == 'H': return 'HALT'
        if e[0] == 'K' and e[4] == B: return (strip(e[2]), e[3])
    return 'T'
if __name__ == '__main__':
    random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    NT = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    for M, t, B in FAM:
        T = kl.tmpl(M, t); ok = bad = to = 0
        for i in range(NT):
            n = random.randint(0, 4)
            ds = [random.randint(1, 4)] + [random.choice([0, 0, 1, 2, 3, 5]) for _ in range(n)] if n or random.random() < .5 else []
            A = random.randint(1, 9) if not strip(ds) or strip(ds)[-1] else random.randint(1, 4)
            p, l = pred(ds, A), literal(M, T, B, ds, A)
            if l == 'T': to += 1; continue
            if p == l: ok += 1
            else: bad += 1; print('BAD', M, ds, A, 'pred', p, 'lit', l)
        print(M, f'ok {ok} bad {bad} timeout {to}', flush=True)
