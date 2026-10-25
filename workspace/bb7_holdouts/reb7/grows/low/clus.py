import idle, sys, itertools
from iso import parse, mirror, mapped, diff
ms = [l.split('\t')[0] for l in open('../low34.txt') if l.strip()]
def dist(a, b):
    ta, n = parse(a); tb, _ = parse(b); best = 99
    for mir in (False, True):
        t2 = mirror(ta) if mir else ta
        for perm in itertools.permutations(range(1, n)):
            d = len(diff(mapped(t2, (0,) + perm), tb))
            if d < best: best = d
    return best
reps = []
fam = {}
for m in ms:
    for i, r in enumerate(reps):
        if dist(m, r) <= 2: fam[m] = i; break
    else:
        reps.append(m); fam[m] = len(reps) - 1
for i, r in enumerate(reps):
    print('F%d' % i, [m for m in ms if fam[m] == i])
