"""kcls.py: classify halt-redirect extensions of the BB(9)/BB(10) champions by their Kd moments.
  python kcls.py EXT.tsv STARTS.txt STEPS > out.tsv
For each machine (renum rows whose E0 enters the new state) and each start (the champion's literal halting
configuration for b), run literally and record: Kd moments (state D, head on 0, blank to the left, Kd ds a b form,
see bb10_champion_1RB1RA_0LF0LJ/kd.py), visits of the new state, the halt.  Output per start: the first Kd moment after
the redirect, the number of Kd moments, the R4 moments (Kd [] 0 x) and the end (H:steps:ones / T / RUNAWAY)."""
import sys
def parse(M):
    t = []
    for q, r in enumerate(M.split('_')):
        for c in (0, 1):
            x = r[3*c:3*c+3]
            if x == '---' or x[2] == 'Z': t.append(None); continue
            if x[0] not in '01' or x[1] not in 'LR' or not ('A' <= x[2] <= 'Z'): raise ValueError('bad %r in %s' % (x, M))
            t.append((int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65))
    return t
def kparse(tape, p, lo, hi):
    if tape[p] != 0 or tape[p+1] != 1: return None
    for i in range(lo, p):
        if tape[i]: return None
    while hi > p and tape[hi] == 0: hi -= 1
    runs = []; cur = 0
    for i in range(p + 1, hi + 1):
        if tape[i]: cur += 1
        else: runs.append(cur); cur = 0
    runs.append(cur)
    if len(runs) < 2: runs.append(0)
    ds = runs[2:]
    while ds and ds[-1] == 0: ds.pop()
    return (tuple(ds), runs[1], runs[0] - 1)
def run(M, word, head, q, N, nst):
    t = parse(M); L = 1 << 22; off = L // 2
    tape = bytearray(L); tape[off:off+len(word)] = bytes(int(c) for c in word)
    h = off + head; lo = off; hi = off + len(word); n = 0
    km = []; r4 = []; newvis = 0; newq = nst - 1
    while n < N:
        c = tape[h]; tr = t[2*q + c]
        if tr is None:
            return ('H', n, sum(tape), '%s%d' % (chr(65+q), c), km, r4, newvis)
        tape[h] = tr[0]; h += tr[1]; q = tr[2]; n += 1
        if h < lo: lo = h
        if h > hi: hi = h
        if h <= 2 or h >= L - 3: return ('W', n, 0, '', km, r4, newvis)
        if q == newq: newvis += 1
        if q == 3 and tape[h] == 0 and tape[h+1] == 1:
            k = kparse(tape, h, lo, hi)
            if k is not None:
                km.append((n, k))
                if not k[0] and k[1] == 0: r4.append(k[2])
    return ('T', n, 0, '', km, r4, newvis)
def short(k):
    ds, a, b = k; s = ','.join(map(str, ds))
    return '[%s]%d,%d' % (s if len(s) < 60 else s[:60] + '..(%d)' % len(ds), a, b)
if __name__ == '__main__':
    ext, stf, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
    starts = [l.split() for l in open(stf) if l.strip()]
    for l in open(ext):
        if l.startswith('#'): continue
        M = l.split('\t')[0].strip(); rows = M.split('_'); nst = len(rows)
        if rows[4][2] != chr(64 + nst): continue
        out = [M]
        for lab, w, hd, qs in starts:
            kind, n, ones, hq, km, r4, nv = run(M, w, int(hd), ord(qs) - 65, N, nst)
            first = short(km[0][1]) if km else '-'
            maxlen = max((len(k[1][0]) for k in km), default=0)
            out.append('%s:%s:%d:%s:K%d:first=%s:maxlen=%d:R4=%s:new=%d' % (lab, kind, n, (str(ones) + hq) if kind == 'H' else '',
                       len(km), first, maxlen, ','.join(map(str, r4[:6])), nv))
        print('\t'.join(out)); sys.stdout.flush()
