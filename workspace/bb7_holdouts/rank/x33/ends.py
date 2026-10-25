import idle  # noqa
import sys
# print the tape (P-inclusive run lengths: runs of 1s separated by single 0s) each time the head is in state A on a blank
# right of everything; start word = '110' + 0^n + '0' + 1^b, head right of it in A.
M = sys.argv[1]; n = int(sys.argv[2]); b = int(sys.argv[3]); steps = int(sys.argv[4]); maxp = int(sys.argv[5])
tr = {}
for q, blk in enumerate(M.split('_')):
    for c in range(2):
        t = blk[3*c:3*c+3]
        tr[(q, c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
w = sys.argv[6] if len(sys.argv) > 6 else '110' + '0' * n + '0' + '1' * b
T = bytearray(1 << 22); off = 1 << 21
for i, ch in enumerate(w): T[off + i] = int(ch)
p = off + len(w); q = 0; lo = off; hi = off + len(w) - 1; np_ = 0
for st in range(steps):
    c = T[p]
    t = tr[(q, c)]
    if t is None:
        print('HALT', st, 'ones', sum(T)); break
    T[p] = t[0]
    if t[0]:
        lo = min(lo, p); hi = max(hi, p)
    p += t[1]; q = t[2]
    if q == 0 and T[p] == 0 and p > hi:
        while not T[hi]: hi -= 1
        if p > hi:
            while not T[lo]: lo += 1
            s = bytes(T[lo:p]).decode('latin1').replace('\x00', '0').replace('\x01', '1')
            runs = [len(x) for x in s.split('0')]
            print(st + 1, 'gap', p - hi - 1, runs[:60], '...' if len(runs) > 60 else '')
            np_ += 1
            if np_ >= maxp: break
