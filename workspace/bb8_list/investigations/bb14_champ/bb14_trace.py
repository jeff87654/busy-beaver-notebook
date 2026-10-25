"""bb14_trace.py MACHINE WORDFILE STATE MAXSTEPS: literal simulation; print every canonical moment
(head in STATE reading 0 with no 1 to its right) with the tape tokenized as D(m)=(10)^m 1 runs,
and the transition counts since the previous moment."""
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
tape = bytearray(6_000_000)
for i, ch in enumerate(w): tape[off + i] = int(ch)
pos = off + len(w); q = ord(q0) - 65; QS = ord(q0) - 65
hi = pos  # one past the rightmost possible 1 (updated as head moves right)

def toks(lo, hi_):
    s = ''.join(str(x) for x in tape[lo:hi_])
    out = []
    i = 0
    if s.startswith('11'):
        out.append('11'); i = 2
    while i < len(s):
        # token (10)^m 1 : count (10) pairs then a 1
        mm = 0; j = i
        while s[j:j + 2] == '10':
            mm += 1; j += 2
        if j < len(s) and s[j] == '1':
            out.append(f'D({mm})'); i = j + 1
        else:
            out.append(f'raw[{s[i:i+16]}...{len(s)-i}b]'); break
    # compress repeats
    comp = []
    for x in out:
        if comp and comp[-1][0] == x: comp[-1][1] += 1
        else: comp.append([x, 1])
    return ' '.join(x if k == 1 else f'{x}^{k}' for x, k in comp)

def moment(st, cnt):
    lo = off
    while lo < pos and tape[lo] == 0: lo += 1
    print(f'step {st} pos={pos-off} wordlen={pos-lo}  {toks(lo, pos)[:220]}', flush=True)
    print('   trans:', ' '.join(f'{k}:{v}' for k, v in sorted(cnt.items()) if v <= 3), flush=True)

cnt = collections.Counter()
nmom = 0
for st in range(N):
    if pos > hi: hi = pos
    if q == QS and tape[pos] == 0 and pos >= hi:
        # no 1 to the right: pos is at/after rightmost reached cell, and tape beyond is blank
        if nmom or st == 0:
            moment(st, cnt); cnt = collections.Counter(); nmom += 1
            if nmom > 14: break
    c = tape[pos]
    if (q, c) not in t:
        print('HALT', st, chr(65 + q) + str(c), flush=True); break
    cnt[chr(65 + q) + str(c)] += 1
    wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
else:
    print('MAX', N, 'moments', nmom, flush=True)
