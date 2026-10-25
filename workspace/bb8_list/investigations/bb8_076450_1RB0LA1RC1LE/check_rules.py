"""Exact literal checks (no acceleration) of the rules of
  main    1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG
  variant 1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG   (F0 = 0LH)

Main: VEc(k, b, r) = 0^inf E>0 1 (1010)^k (01)^b r   (= X(2k, b, r))
  IN  : VEc(k+1, b+1, r)       -> VEc(k+2, b, r)          (r arbitrary, never visited)
  S5  : VEc(k+1, 0, 11111 r)   -> VEc(3, 2k+2, r)         (r arbitrary, never visited)
  E1w : VEc(k+1, 0, 1 01)      -> VEc(2, 0, 1^(4k+7) 01)
  Family VF(m, q) = VEc(5m+2, 0, (11111)^q 1 01):
  Round: VF(m, q+1) -> VF(2m+1, q);  Reset: VF(m, 0) -> VF(0, 4m+2)
Variant: Ec(k, b, r) = 0^inf E>0 1 1 0 (1010)^k (01)^b r   (= X(2k+1, b, r))
  IN  : Ec(k, b+1, r) -> Ec(k+1, b, r);  S5 : Ec(k, 0, 11111 r) -> Ec(2, 2k+2, r)   (r never visited)
  S4  : Ec(k, 0, 1111)          -> Ec(2, 2k+1, e)
  Z0w : Ec(k, 0, e)             -> Ec(1, 0, 1^(4k+3) 01)
  E3w : Ec(k, 0, 111 01)        -> Ec(1, 0, 1^(4k+3) 0 11111 01)
  E2ww: Ec(k, 0, 11 0 11111 01) -> Ec(1, 0, 1^(4k+9) 01)
  E2w : Ec(k, 0, 11 01)         -> Ec(1, 0, 1^(4k+5))
  Family Fa(m, q, t) = Ec(5m+1, 0, (11111)^q t), Fb(m) = Ec(5m, 0, e):
  T1: Fa(m,q+1,t) -> Fa(2m+1,q,t)   (t = each tail below)   T2 : Fa(m,0,1111) -> Fb(2m+1)
  T0w: Fa(m,0,11 01) -> Fa(0,4m+1,1111)   T3w: Fa(m,0,111 01) -> Fa(0,4m+1,11 0 11111 01)
  T2w: Fa(m,0,11 0 11111 01) -> Fa(0,4m+2,111 01)   T4w: Fb(m) -> Fa(0,4m,111 01)
All tails end in 0^inf (e = empty). Each run goes from the start to the FIRST later configuration with state E
reading 0 and a blank tape to its left whose word equals the target; for arbitrary r no cell of r may be visited.
Usage: python check_rules.py [out.json]
"""
import json, random, sys
from cr_lib import run, table

MAIN = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG"
VAR = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG"
TM_, TV = table(MAIN), table(VAR)


def W(s):
    return [int(c) for c in s]


def mword(k, b, tail):
    return [1] + [1, 0, 1, 0] * k + [0, 1] * b + list(tail)


def vword(k, b, tail):
    return [1, 1, 0] + [1, 0, 1, 0] * k + [0, 1] * b + list(tail)


VT = {'0': W('1101'), '3': W('11101'), '2': W('1101111101'), '4': W('1111')}


def main():
    random.seed(20260928)
    out = {}
    fails = total = 0

    def rec(name, sw, tw, rl, TT, maxsteps=10**6, **info):
        nonlocal fails, total
        steps, ok, vis = run(sw, tw, rl, maxsteps, TT=TT)
        good = (ok is True) and not vis
        total += 1
        if not good:
            fails += 1
            print('FAIL', name, info, ok, 'visited r' if vis else '', steps)
        out.setdefault(name, []).append(dict(info, steps=steps, ok=good))

    def rand_ctx():
        return [random.randint(0, 1) for _ in range(random.randint(1, 8))] + [1]

    for k in range(0, 40):
        for ci in range(3):
            r = [] if ci == 0 else rand_ctx()
            cs = ''.join(map(str, r))
            for b in range(0, 4):
                rec('M.IN', mword(k + 1, b + 1, r), mword(k + 2, b, r), len(r), TM_, k=k, b=b, ctx=cs)
                rec('V.IN', vword(k, b + 1, r), vword(k + 1, b, r), len(r), TV, k=k, b=b, ctx=cs)
            rec('M.S5', mword(k + 1, 0, [1] * 5 + r), mword(3, 2 * k + 2, r), len(r), TM_, k=k, ctx=cs)
            rec('V.S5', vword(k, 0, [1] * 5 + r), vword(2, 2 * k + 2, r), len(r), TV, k=k, ctx=cs)
        rec('M.E1w', mword(k + 1, 0, W('101')), mword(2, 0, [1] * (4 * k + 7) + W('01')), 0, TM_, k=k)
        rec('V.S4', vword(k, 0, W('1111')), vword(2, 2 * k + 1, []), 0, TV, k=k)
        rec('V.Z0w', vword(k, 0, []), vword(1, 0, [1] * (4 * k + 3) + W('01')), 0, TV, k=k)
        rec('V.E3w', vword(k, 0, W('11101')), vword(1, 0, [1] * (4 * k + 3) + W('01111101')), 0, TV, k=k)
        rec('V.E2ww', vword(k, 0, W('1101111101')), vword(1, 0, [1] * (4 * k + 9) + W('01')), 0, TV, k=k)
        rec('V.E2w', vword(k, 0, W('1101')), vword(1, 0, [1] * (4 * k + 5)), 0, TV, k=k)

    def vf(m, q):
        return mword(5 * m + 2, 0, [1] * (5 * q) + W('101'))

    def fa(m, q, t):
        return vword(5 * m + 1, 0, [1] * (5 * q) + VT[t])

    def fb(m):
        return vword(5 * m, 0, [])

    for m in range(0, 8):
        for q in range(0, 4):
            rec('M.Round', vf(m, q + 1), vf(2 * m + 1, q), 0, TM_, 10**8, m=m, q=q)
            for t in VT:
                rec('V.T1', fa(m, q + 1, t), fa(2 * m + 1, q, t), 0, TV, 10**8, m=m, q=q, t=t)
        rec('M.Reset', vf(m, 0), vf(0, 4 * m + 2), 0, TM_, 10**8, m=m)
        rec('V.T2', fa(m, 0, '4'), fb(2 * m + 1), 0, TV, 10**8, m=m)
        rec('V.T0w', fa(m, 0, '0'), fa(0, 4 * m + 1, '4'), 0, TV, 10**8, m=m)
        rec('V.T3w', fa(m, 0, '3'), fa(0, 4 * m + 1, '2'), 0, TV, 10**8, m=m)
        rec('V.T2w', fa(m, 0, '2'), fa(0, 4 * m + 2, '3'), 0, TV, 10**8, m=m)
        rec('V.T4w', fb(m), fa(0, 4 * m, '3'), 0, TV, 10**8, m=m)
    for name in out:
        print('%-8s %d/%d ok' % (name, sum(1 for x in out[name] if x['ok']), len(out[name])))
    print('total %d cases, %d failures' % (total, fails))
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], 'w'), indent=0)


if __name__ == '__main__':
    main()
