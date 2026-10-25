import idle  # noqa
import sys
# P-inclusive K-trace from blank: at each state-A right-end event print run list when the prefix (all but last 2) changes
M = sys.argv[1]; steps = int(sys.argv[2]); maxp = int(sys.argv[3]); Q = sys.argv[4] if len(sys.argv) > 4 else 'A'
tr = {}
for q, blk in enumerate(M.split('_')):
    for c in range(2):
        t = blk[3*c:3*c+3]
        tr[(q, c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
T = bytearray(1 << 24); off = 1 << 23
p = off; q = 0; lo = off; hi = off - 1; np_ = 0; last = None; qq = ord(Q) - 65
for st in range(steps):
    c = T[p]
    t = tr[(q, c)]
    if t is None:
        print('HALT', st, 'ones', sum(T)); break
    T[p] = t[0]
    if t[0]:
        if hi < lo: lo = hi = p
        lo = min(lo, p); hi = max(hi, p)
    p += t[1]; q = t[2]
    if q == qq and T[p] == 0 and p > hi and hi >= lo:
        while not T[hi]: hi -= 1
        while not T[lo]: lo += 1
        s = bytes(T[lo:hi + 1]).replace(b'\x00', b'0').replace(b'\x01', b'1').decode()
        runs = [len(x) for x in s.split('0')]
        key = tuple(runs[:-2])
        if key != last:
            last = key
            def rl(r):
                o = []; i = 0
                while i < len(r):
                    j = i
                    while j < len(r) and r[j] == r[i]: j += 1
                    o.append('%d' % r[i] + ('^%d' % (j - i) if j > i + 1 else '')); i = j
                return ','.join(o)
            print(st + 1, 'gap', p - hi - 1, '[' + rl(runs) + ']')
            np_ += 1
            if np_ >= maxp: break
