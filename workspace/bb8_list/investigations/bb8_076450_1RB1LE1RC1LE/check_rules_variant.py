"""Exact literal checks (no acceleration) of the rules of the F0 variant
1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG.

VEc(k, b, r) = 0^inf E>0 1 (1010)^k (01)^b r            (= X(2k, b, r))
Phase rules (r arbitrary and never visited, unless it is 0^inf):
  IN  : VEc(k+1, b+1, r)          -> VEc(k+2, b, r)
  S5  : VEc(k+1, 0, 11111 r)      -> VEc(3, 2k+2, r)
  S4  : VEc(k+1, 0, 1111 r)       -> VEc(3, 2k+1, 0 r)
  E2b : VEc(k+1, 0, 11)           -> VEc(2, 0, 1^(4k+4))
  E1b : VEc(k+1, 0, 1)            -> VEc(2, 0, 1^(4k+7))
  E3b : VEc(k+1, 0, 111)          -> VEc(2, 0, 1^(4k+3) 010111)
  E2w : VEc(k+1, 0, 11 010111)    -> VEc(2, 0, 1^(4k+5) 0111)
  E0x : VEc(k+1, 0, 0 0111)       -> VEc(2, 0, 1^(4k+6))
Family VF(m, q, t) = VEc(5m+2, 0, (11111)^q t):
  R   : VF(m, q+1, t)             -> VF(2m+1, q, t)       (t = each of the five tails below)
  VE2b: VF(m, 0, 11)              -> VF(0, 4m+1, 111)
  VE3b: VF(m, 0, 111)             -> VF(0, 4m+1, 11 010111)
  VE2w: VF(m, 0, 11 010111)       -> VF(0, 4m+1, 1111 0111)
  VE4w: VF(m, 0, 1111 0111)       -> VF(0, 8m+5, 1)
  VE1b: VF(m, 0, 1)               -> VF(0, 4m+2, 1)
Each run goes from the start to the FIRST later configuration (state E reading 0, blank tape to the left) whose
word equals the target; for arbitrary r no cell of r may be visited. Tails end in 0^inf.
Usage: python check_rules_variant.py [out.json]
"""
import json, random, sys
from check_rules import run, table

VAR = "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG"
TV = table(VAR)


def W(s):
    return [int(c) for c in s]


def vword(k, b, tail):
    return [1] + [1, 0, 1, 0] * k + [0, 1] * b + list(tail)


TAILS = {'11': W('11'), '111': W('111'), '11w': W('11010111'), '1111w': W('11110111'), '1': W('1')}


def main():
    random.seed(4242)
    out = {}
    fails = 0
    total = 0

    def rand_ctx():
        return [random.randint(0, 1) for _ in range(random.randint(1, 8))] + [1]

    for k in range(0, 40):
        for ci in range(3):
            r = [] if ci == 0 else rand_ctx()
            cases = []
            for b in range(0, 4):
                cases.append(('IN', vword(k + 1, b + 1, r), vword(k + 2, b, r), len(r)))
            cases.append(('S5', vword(k + 1, 0, [1] * 5 + r), vword(3, 2 * k + 2, r), len(r)))
            cases.append(('S4', vword(k + 1, 0, [1] * 4 + r), vword(3, 2 * k + 1, [0] + r), len(r)))
            if ci == 0:
                cases.append(('E2b', vword(k + 1, 0, W('11')), vword(2, 0, [1] * (4 * k + 4)), 0))
                cases.append(('E1b', vword(k + 1, 0, W('1')), vword(2, 0, [1] * (4 * k + 7)), 0))
                cases.append(('E3b', vword(k + 1, 0, W('111')), vword(2, 0, [1] * (4 * k + 3) + W('010111')), 0))
                cases.append(('E2w', vword(k + 1, 0, W('11010111')), vword(2, 0, [1] * (4 * k + 5) + W('0111')), 0))
                cases.append(('E0x', vword(k + 1, 0, W('00111')), vword(2, 0, [1] * (4 * k + 6)), 0))
            for name, sw, tw, rl in cases:
                steps, ok, vis = run(sw, tw, rl, 10**6, TT=TV)
                good = (ok is True) and not vis
                total += 1
                if not good:
                    fails += 1
                    print('FAIL', name, 'k=%d' % k, 'ctx', r, ok, 'visited r' if vis else '', steps)
                out.setdefault(name, []).append(dict(k=k, ctx=''.join(map(str, r)), steps=steps, ok=good))

    def vf(m, q, t):
        return vword(5 * m + 2, 0, [1] * (5 * q) + TAILS[t])

    for m in range(0, 6):
        for q in range(0, 3):
            for t in TAILS:
                cases = [('R', vf(m, q + 1, t), vf(2 * m + 1, q, t))]
                if q == 0:
                    nxt = {'11': ('VE2b', 0, 4 * m + 1, '111'), '111': ('VE3b', 0, 4 * m + 1, '11w'),
                           '11w': ('VE2w', 0, 4 * m + 1, '1111w'), '1111w': ('VE4w', 0, 8 * m + 5, '1'),
                           '1': ('VE1b', 0, 4 * m + 2, '1')}[t]
                    cases.append((nxt[0], vf(m, 0, t), vf(nxt[1], nxt[2], nxt[3])))
                for name, sw, tw in cases:
                    steps, ok, vis = run(sw, tw, 0, 10**8, TT=TV)
                    total += 1
                    good = ok is True
                    if not good:
                        fails += 1
                        print('FAIL', name, m, q, t, ok, steps)
                    out.setdefault(name, []).append(dict(m=m, q=q, t=t, steps=steps, ok=good))
    for name in out:
        print('%-4s %d/%d ok' % (name, sum(1 for x in out[name] if x['ok']), len(out[name])))
    print('total %d cases, %d failures' % (total, fails))
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], 'w'), indent=0)


if __name__ == '__main__':
    main()
