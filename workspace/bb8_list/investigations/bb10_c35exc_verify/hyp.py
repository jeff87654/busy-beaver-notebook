"""hyp.py -- test a hypothesised rule: python hyp.py "LHS" "RHS" with tokens separated by commas.
symbols: integers, v (big counter, values 9..14), j (ones count 0..3 -> written as 1^j), y (accumulator),
RHS may use expressions in v, y like v-4, 2*y+4."""
import sys, itertools
from lib import bforms, ctok, M10
P = [2, 1, 1, 0, 2, 1, 0, 1]
lhs, rhs = sys.argv[1], sys.argv[2]
jr = [int(a) for a in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0, 1, 2, 3]
kr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else [0]
def expand(pat, env):
    out = []
    for tok in pat.split(','):
        tok = tok.strip()
        if tok == '1^j': out += [1] * env['j']
        elif tok == '1^k': out += [1] * env['k']
        elif tok == '1^(k-1)': out += [1] * (env['k'] - 1)
        else: out.append(int(eval(tok, {}, env)))
    return out
bad = tot = 0
for v in (9, 10, 11, 13, 20):
    for j in jr:
        for k in kr:
            for y in (4, 5, 6, 7, 8, 16):
                env = dict(v=v, j=j, y=y, k=k)
                L = P + [25] + expand(lhs, env)
                exp = P + [25] + expand(rhs, env)
                bf, end = bforms(M10, L, 2 * 10**6, maxsnap=2)
                got = bf[1][1] if len(bf) > 1 else None
                tot += 1
                if got != exp:
                    bad += 1
                    if bad < 6: print('FAIL', env, ctok(L[9:]), '->', ctok(got[9:]) if got else end[:2], 'exp', ctok(exp[9:]))
print('tested', tot, 'failures', bad)
