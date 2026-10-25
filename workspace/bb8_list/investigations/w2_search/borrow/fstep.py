"""fstep.py: one follower stage (literal stage + jump) as a pure function, for lazy enumeration."""
import idle  # noqa: F401  (Idle priority)

import sys, os
from nfol import run_stage, rle, mf35, mf35g, Aff, Fail, jump
MM = 2520; LB = 19
SUF = '1010'

def stage(M, word, maxs=2 * 10**7, policy='std', bigk=1):
    """returns (kind, data):
       ('H', (state, sym, steps, ones)) undefined slot read;  ('T'|'W', None);
       ('K', (digits+[a,r], far, newword, event, zeros_after))"""
    out, used = run_stage(M, word, len(word), 'G', maxs)
    f = out.split()
    if not f:
        return 'FAIL', None
    if f[0] == 'H':
        return 'H', (f[2], int(f[3]), int(f[1]), int(f[4]))
    if f[0] in ('T', 'W', 'X'):
        return f[0], None
    parts = out.split('|')
    toks = [int(x) for x in parts[1].split()]
    far = parts[2].strip() if len(parts) > 2 else ''
    digits = toks[2:][::-1]
    ent = []
    for m in digits:
        if ent and ent[-1][1] == m:
            ent[-1][2] += 1
        else:
            ent.append(['D', m, 1])
    left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
    try:
        items, newp, info = jump(left, [], {}, 1)
    except (Fail, AssertionError, RuntimeError, RecursionError, KeyError, ZeroDivisionError) as ex:
        return 'JF', (digits + [toks[1], toks[0]], far, str(ex)[:60])
    vals = {}
    for p, v in newp.items():
        base = mf35.rep(v, MM, LB)
        vals[p] = base if (v.exact or policy == 'std') else base + MM * bigk
    new = []
    for e in items:
        m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
        c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
        new += [m] * c
    if len(new) >= 2 and new[-1] > 2000 and policy == 'std':
        new[-1] = LB + ((new[-1] - LB) % MM)
    nz = 0
    for m in new[:-2][::-1]:
        if m != 1: break
        nz += 1
    newword = far + mf35.word_of_tokens(new) + SUF
    return 'K', (digits + [toks[1], toks[0]], far, newword, info.get('event'), nz, new)
