from fw import *
for mach, lab in [(GH8, 'GH8'), (M10, 'n1')]:
    s = Server(mach, 'BfH', 1)
    x = s.job('0', 0, 'A', 10 ** 7)[-1]
    tot = x['step']; L, A = bparse(x['word'], x['rel'])
    seen = []
    while tot < 60000:
        seen.append((tot, L, A))
        w, h, q = bword(L, A)
        x = s.job(w, h, q, 10 ** 8)[-1]
        if x['kind'] != 'BF':
            print(lab, 'non-BF', x['kind']); break
        tot += x['step']; L, A = bparse(x['word'], x['rel'])
    for t, L, A in seen:
        if len(L) >= 30 and (L[0] == 7 or L == [4] * 36):
            print(lab, t, '[%s | %d]' % (fmt(L), A))
    s.close()
