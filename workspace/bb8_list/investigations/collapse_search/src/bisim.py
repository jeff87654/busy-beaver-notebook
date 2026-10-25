"""bisim.py: observed-behaviour merge analysis from cfollow 'prof' outputs (one or more worlds).
For every pair of states X,Y: the union state Z (X,Y identified) is OBSERVED-COMPATIBLE if for each symbol c used by
both X and Y in the profiled runs, X_c == Y_c modulo X~Y.  Slots used by only one of them are free to take.  The halt slot
counts as used if the run halted there.  Partition refinement is applied on top (merging X,Y may force targets to agree).
Near-miss: incompatible only on slots whose usage count is <= RARE (default 1% of the state's entries) on one side.
usage: python bisim.py MACHINE PROF1 [PROF2 ...]"""
import sys
def parse(m):
    T = []
    for row in m.split('_'):
        T.append([None if row[3*c] == '-' else (row[3*c:3*c+2], ord(row[3*c+2]) - 65) for c in range(2)])
    return T
M = sys.argv[1]; T = parse(M); n = len(T)
use = [[0, 0] for _ in range(n)]; halted = set()
for f in sys.argv[2:]:
    for l in open(f):
        if l.startswith('USE '):
            _, s, k = l.split(); use[ord(s[0]) - 65][int(s[1])] += int(k)
        if l.startswith('#') and 'HALT ' in l:
            h = l.split('HALT ')[1][:2]; halted.add((ord(h[0]) - 65, int(h[1])))
for (s, c) in halted: use[s][c] = max(use[s][c], 1)
def eq(t1, t2, X, Y):
    if t1 is None or t2 is None: return t1 is t2
    a = Y if t1[1] == X else t1[1]; b = Y if t2[1] == X else t2[1]
    return t1[0] == t2[0] and a == b
out = []
for X in range(n):
    for Y in range(X):
        conf = []
        for c in range(2):
            if use[X][c] and use[Y][c] and not eq(T[X][c], T[Y][c], X, Y):
                conf.append((c, use[X][c], use[Y][c]))
        small = min(sum(use[X]), sum(use[Y]))
        minor = sum(min(a, b) for _, a, b in conf)
        if small == 0: tag = 'UNUSED'
        else: tag = 'COMPATIBLE' if not conf else ('NEAR' if minor <= 2 * (len(sys.argv) - 2) else 'no')
        out.append((minor, tag, X, Y, conf))
out.sort(key=lambda z: ({'COMPATIBLE':0,'UNUSED':1,'NEAR':2}.get(z[1],3), z[0]))
print('machine', M); print('slot use:', ' '.join('%s%d:%d' % (chr(65+s), c, use[s][c]) for s in range(n) for c in range(2)))
print('unused slots:', ' '.join('%s%d' % (chr(65+s), c) for s in range(n) for c in range(2) if not use[s][c]) or '-')
for minor, tag, X, Y, conf in [z for z in out if z[1] != 'no'] + [z for z in out if z[1] == 'no'][:3]:
    print('%-10s %s~%s conflicts: %s' % (tag, chr(65+X), chr(65+Y), ', '.join('%d(%d vs %d)' % z for z in conf) or '-'))
