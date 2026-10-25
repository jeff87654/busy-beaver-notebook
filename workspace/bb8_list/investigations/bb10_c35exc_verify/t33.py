import random, pickle
import engine, rules, oracle, tcycler
from num import H, M, res, is_huge
from tower import tower_res
from lib import word, run, M10
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
try:
    engine.R(s, top=True)
except rules.Unknown as e:
    lst = e.lst
print('final list (%d tokens):' % len(lst))
print(' '.join(('H[r3=%d,r6=%d,r4=%d,r5=%d]' % (res(v, 3), res(v, 6), res(v, 4), res(v, 5))) if is_huge(v) else str(v) for v in lst))
pickle.dump([('H', v.r) if is_huge(v) else v for v in lst], open('pre_runaway.pkl', 'wb'))
# literal check with representatives
P = [2, 1, 1, 0, 2, 1, 0, 1]
rnd = random.Random(3)
results = []
for trial in range(12):
    rep = []
    for i, v in enumerate(lst):
        if is_huge(v):
            if i == len(lst) - 1:
                rep.append(res(v, 6) + 6 * rnd.randint(3, 15))
            else:
                rep.append(res(v, 3) + 3 * rnd.randint(8, 30))
        else:
            rep.append(v)
    ctx = P + [rnd.choice([41, 44, 47]), 3] + [1] * rnd.randint(0, 4)
    toks = ctx + rep
    tcycler.hist.clear()
    r = tcycler.check(M10, word(toks), 'G', '0', W=150, maxsteps=4 * 10**6)
    results.append(r[0])
    print(trial, r)
print(results)
