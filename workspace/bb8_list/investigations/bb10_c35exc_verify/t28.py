import random
import engine, rules
from num import H, M, r1star, is_huge, LIM
random.seed(7)
# (a) residue arithmetic of r1star against exact big integers
bad = 0
for trial in range(300):
    x = random.randint(3, 3000); y = random.randint(2, 10**6)
    xe, y2 = r1star(x, y)
    v = (x - xe) // 3
    exact = (y + 8) * 2**v - 8
    got = y2.r if is_huge(y2) else y2
    if exact % M != got % M: bad += 1
    # huge x path: x as H with the same residue (x >= LIM not true, but residue logic): use x + k*M*3 equivalents
    X = x + 3 * M * random.randint(1, 5)   # same residue mod 3M -> v differs by a multiple of M
    xe2, y3 = r1star(H(X), y)
    v2 = (X - xe2) // 3
    exact2 = ((y + 8) * pow(2, v2, M) - 8) % M
    if y3.r != exact2: bad += 1
print('r1star residue mismatches', bad)
# (b) engine jumps vs brute force with the same rule arithmetic (counters 1000..4000)
agree = dis = skip = 0
for trial in range(200):
    c = random.randint(1000, 4000)
    body = [random.choice([1, 1, 4, 7, 3, 6, 5, 2, 0]) for _ in range(random.randint(1, 3))]
    s = [c] + body + [0, random.randint(2, 9)]
    t = list(s); n = 0; ok = True
    try:
        while True:
            try:
                ev = rules.classify(t)
            except rules.Need:
                break
            t = ev.newlist; n += 1
            if n > 300000: ok = False; break
    except rules.Unknown:
        ok = False
    if not ok: skip += 1; continue
    engine.memo.clear()
    try:
        r = engine.R(s, top=True)
    except rules.Unknown:
        skip += 1; continue
    if [v.r if is_huge(v) else v for v in r] == [v.r if is_huge(v) else v for v in t]: agree += 1
    else:
        dis += 1
        if dis < 4: print('DIS', s, r, t)
print('jump test agree', agree, 'disagree', dis, 'skip', skip, engine.stats)
