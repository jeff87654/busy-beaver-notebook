"""bb14_trace2.py MACHINE WORDFILE STATE MAXSTEPS: literal simulation; at every canonical moment
(head in STATE on 0 at the right frontier) compute the token signature of the tape and print only
when the signature's shape (token values, with run lengths) changes, with all transition counts."""
import ctypes as _ct, sys as _sys
if _sys.platform == 'win32':
    try: _ct.windll.kernel32.SetPriorityClass(_ct.windll.kernel32.GetCurrentProcess(), 0x40)
    except Exception: pass

import sys, collections
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb10_bb7_descendants/loopvar')
from prof import parse

m, w, q0, N = sys.argv[1], open(sys.argv[2]).read().strip(), sys.argv[3], int(sys.argv[4])
t = parse(m)
off = 2_000_000
tape = bytearray(8_000_000)
for i, ch in enumerate(w): tape[off + i] = int(ch)
pos = off + len(w); q = ord(q0) - 65; QS = q
hi = pos

def sig(lo, hi_):
    s = ''.join(str(x) for x in tape[lo:hi_])
    vals = []
    i = 2 if s.startswith('11') else 0
    while i < len(s):
        mm = 0; j = i
        while s[j:j + 2] == '10':
            mm += 1; j += 2
        if j < len(s) and s[j] == '1':
            vals.append(mm); i = j + 1
        else:
            vals.append(('raw', len(s) - i)); break
    comp = []
    for x in vals:
        if comp and comp[-1][0] == x: comp[-1][1] += 1
        else: comp.append([x, 1])
    return tuple((x, k) for x, k in comp)

def show(sg):
    return ' '.join((f'D({x})' if k == 1 else f'D({x})^{k}') if isinstance(x, int) else f'{x}' for x, k in sg)

cnt = collections.Counter(); last = None; npr = 0
for st in range(N):
    if pos > hi: hi = pos
    if q == QS and tape[pos] == 0 and pos >= hi:
        lo = off
        while lo < pos and tape[lo] == 0: lo += 1
        sg = sig(lo, pos)
        shape = tuple((x if isinstance(x, tuple) else ('D' if x > 4 else x), k) for x, k in sg)
        if shape != last:
            print(f'step {st} len={pos-lo} {show(sg)[:240]}', flush=True)
            print('   trans:', ' '.join(f'{k}:{v}' for k, v in sorted(cnt.items())), flush=True)
            cnt = collections.Counter(); last = shape; npr += 1
            if npr > 40: break
    c = tape[pos]
    if (q, c) not in t:
        print('HALT', st, chr(65 + q) + str(c), flush=True); break
    cnt[chr(65 + q) + str(c)] += 1
    wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
else:
    print('MAX', N, flush=True)
