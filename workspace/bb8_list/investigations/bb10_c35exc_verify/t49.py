import random, pickle, tcycler
from lib import word, run, M10
lst = pickle.load(open('pre_runaway.pkl', 'rb'))
P = [2, 1, 1, 0, 2, 1, 0, 1]
rnd = random.Random(17)
for trial in range(4):
    rep = []
    for i, v in enumerate(lst):
        if isinstance(v, tuple):
            r = v[1]
            if i == len(lst) - 1:
                rep.append(r % 6 + 6 * rnd.randint(2, 12))          # accumulator Y: small (16..76)
            else:
                rep.append(r % 3 + 3 * rnd.randint(300, 1000))      # level tokens: large (900..3000)
        else:
            rep.append(v)
    toks = P + [47, 3, 1, 1, 1] + rep
    tcycler.hist.clear()
    r = tcycler.check(M10, word(toks), 'G', '0', W=200, maxsteps=6 * 10**6)
    print('Y=%d a=%d' % (rep[-1], rep[-7]), r)
