import pickle, itertools
import tcycler
from lib import word, run, M10, tokens, ctok
lst = pickle.load(open('pre_runaway.pkl', 'rb'))
P = [2, 1, 1, 0, 2, 1, 0, 1]
# minimal local test: [ctx, Hm(=a, = 0 mod 3), 3, 1, 1, 0, 0, Y] with a left neighbour list like the real one
def outcome(a, Y, ctx_h=31):
    toks = P + [44, 3, 1, 1] + [lst[0][1] % 3 + 30, 0, ctx_h, 0, a, 3, 1, 1, 0, 0, Y]
    tcycler.hist.clear()
    r = tcycler.check(M10, word(toks), 'G', '0', W=150, maxsteps=2 * 10**6)
    if r[0] != 'TCYCLER':
        snaps, end = run(M10, word(toks), 'G', '0', 2 * 10**6, ['snap=G0', 'bform', 'maxsnap=3'])
        return 'B:' + (ctok(tokens(snaps[1][1])[-6:]) if len(snaps) > 1 else end[0])
    return 'TC'
for a in (12, 15, 18, 24, 30):
    row = []
    for Y in range(4, 64, 2):
        o = outcome(a, Y)
        row.append('%d:%s' % (Y, 'T' if o == 'TC' else 'b'))
    print('a=%d' % a, ' '.join(row))
