import idle, sys, random
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\f3')
import fx, rules
m, O, Q = sys.argv[1], sys.argv[2], sys.argv[3]
TL = eval(sys.argv[4]); G = int(sys.argv[5])
fx.MACH['S'] = (m, O, Q, TL, G); rules.RULES['S'] = rules.RULES[sys.argv[6]]
evs = fx.sim('S', ['BLANK'], maxs=10**9, maxev=40)[0]
for e in evs:
    if e[0] == 'E':
        pc = fx.parse_ev('S', e); print('  E', e[1], (fx.rle(pc[0]) or '-', pc[1]) if pc else ('raw', e[2], e[3][:80]))
    else: print(' ', ' '.join(e))
lists = [[], [0], [0, 0], [1, 0, 0], [2, 0, 0], [3], [1, 0], [2, 1, 1, 1]]
for ds in lists:
    res = fx.nxt('S', [(ds, a) for a in range(0, 14)], maxs=3 * 10**8)
    out = []
    for a, r in enumerate(res):
        if r[0] == 'K': out.append('%d:[%s;%d]' % (a, fx.rle(r[1]) or '-', r[2]))
        elif r[0] == 'H': out.append('%d:H' % a)
        else: out.append('%d:%s' % (a, r[0]))
    print(fx.rle(ds) or '-', ' '.join(out)[:400])
random.seed(3); cnt = {}
for t in range(int(sys.argv[7]) if len(sys.argv) > 7 else 30):
    n = random.randint(0, 6); ds = [0 if random.random() < 0.45 else random.randint(1, 4) for _ in range(n)]; a = random.randint(0, 9)
    res, info = rules.check('S', ds, a); cnt[res] = cnt.get(res, 0) + 1
    if res == 'MISS' and cnt[res] <= 4: print('  MISS', ds, a, str(info)[:250])
print('rulecheck', cnt)
