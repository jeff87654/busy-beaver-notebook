import idle, sys, random
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\f3')
import fx, rules
from iso import parse, mirror, mapped, diff, PAR  # noqa
import itertools
def bestmap(m, parent):
    ts, n = parse(m); tp, _ = parse(PAR[parent]); best = None
    for mir in (False, True):
        t2 = mirror(ts) if mir else ts
        for perm in itertools.permutations(range(n)):
            d = diff(mapped(t2, perm), tp)
            if best is None or len(d) < len(best[0]): best = (d, mir, perm)
    return best
def setup(m, parent, tag):
    d, mir, perm = bestmap(m, parent)
    PM, O, Q, TL, G = fx.MACH[parent]
    inv = {perm[s]: s for s in range(len(perm))}
    O2 = O if not mir else ('L' if O == 'R' else 'R')
    Q2 = chr(65 + inv[ord(Q) - 65])
    fx.MACH[tag] = (m, O2, Q2, TL, G)
    rules.RULES[tag] = rules.RULES[parent]
    return d, mir, perm
if __name__ == '__main__':
    m, parent = sys.argv[1], sys.argv[2]
    maxs = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**9
    ncheck = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    d, mir, perm = setup(m, parent, 'S')
    print('map', parent, 'mir', mir, 'start->', chr(65 + perm[0]), 'ndiff', len(d), fx.MACH['S'])
    evs = fx.sim('S', ['BLANK'], maxs=maxs, maxev=60)[0]
    for e in evs:
        if e[0] == 'E':
            pc = fx.parse_ev('S', e)
            print('  E', e[1], (fx.rle(pc[0]) or '-', pc[1]) if pc else ('raw', e[2], e[3][:80]))
        else: print(' ', ' '.join(e))
    if ncheck:
        random.seed(7); cnt = {}
        for t in range(ncheck):
            n = random.randint(0, 6)
            ds = [0 if random.random() < 0.45 else random.randint(1, 4) for _ in range(n)]
            a = random.randint(0, 9)
            res, info = rules.check('S', ds, a)
            cnt[res] = cnt.get(res, 0) + 1
            if res == 'MISS' and cnt[res] <= 6: print('  MISS', ds, a, str(info)[:300])
        print('  rulecheck', cnt)
