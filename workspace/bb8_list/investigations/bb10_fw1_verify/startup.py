from fw import *
s = Server(M10, 'Bf', 1)
x = s.job('0', 0, 'A', 10 ** 7)[-1]
tot = x['step']; L, A = bparse(x['word'], x['rel'])
seen = []
while tot < 50000:
    seen.append((tot, L, A))
    w, h, q = bword(L, A)
    x = s.job(w, h, q, 10 ** 8)[-1]
    if x['kind'] != 'BF':
        print('non-BF', x['kind']); break
    tot += x['step']; L, A = bparse(x['word'], x['rel'])
for t, L, A in seen:
    if t in (6413, 47897) or (len(L) >= 30 and t < 7000):
        print(t, '[%s | %d]' % (fmt(L), A))
s.close()
