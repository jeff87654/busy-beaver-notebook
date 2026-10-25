import random, pickle
import tcycler
from lib import word, run, M10, tokens, ctok, rle
lst = pickle.load(open('pre_runaway.pkl', 'rb'))
P = [2, 1, 1, 0, 2, 1, 0, 1]
rnd = random.Random(3)
from num import M
for trial in range(12):
    rep = []
    for i, v in enumerate(lst):
        if isinstance(v, tuple):
            r = v[1]
            if i == len(lst) - 1:
                rep.append(r % 6 + 6 * rnd.randint(3, 15))
            else:
                rep.append(r % 3 + 3 * rnd.randint(8, 30))
        else:
            rep.append(v)
    ctx = P + [rnd.choice([41, 44, 47]), 3] + [1] * rnd.randint(0, 4)
    if trial not in (0, 8):
        continue
    toks = ctx + rep
    print(trial, 'ctx', ctx[8:], 'rep tail', rep[-8:], 'Y=%d' % rep[-1])
    snaps, end = run(M10, word(toks), 'G', '0', 3 * 10**7, ['snap=G0', 'bform', 'maxsnap=20'])
    for s in snaps[1:8]:
        print('   B-form', s[0], ctok(tokens(s[1])[-14:]))
    print('   end', end[0], end[1], rle(end[2])[-120:], '|', end[3], '|', end[4][:40])
