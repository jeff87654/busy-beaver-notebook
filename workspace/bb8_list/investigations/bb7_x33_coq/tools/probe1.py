import idle  # noqa
from sim import nxt
# R3 threshold: runs = [top..., y+1, 0^k, a=0, b]
for top in ([3], [2], [1], [2, 5]):
    for k in range(1, 6):
        res = []
        for b in range(0, 2 * k + 4):
            o = nxt(top + [0] * k + [0, b], 10**6)
            res.append('%d:%s' % (b, (o[2] if o[0] == 'K' else o[0] + str(o[1]) + ('/%d' % o[2] if o[0]=='HALT' else ''))))
        print(top, k, ' '.join(res))
# true exhaustion [B]
for B in range(0, 14):
    o = nxt([B], 10**6)
    print('B', B, o[0], o[1], o[2] if o[0] != 'TIMEOUT' else '')
