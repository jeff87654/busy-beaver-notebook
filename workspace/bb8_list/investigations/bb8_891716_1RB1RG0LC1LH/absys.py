"""Abstract K-level system of the 891716 machine and comparison with the literal machine (ksim.exe).
State (par, ds, a, b): par 'o' = marker + tokens (Ko), 'e' = tokens only (Ke); ds = [d1..dn], dn nearest the head.
  R1 : a > 0                         -> (ds, a-1, b+2)
  R23: a = 0, last nonzero digit y+1 followed by k zeros:
        k = 0: (.., y+1; 0; b) -> (.., y; b+2; 0)        k >= 1: (.., y+1, 0^k; 0; b) -> (.., y, b+2, 0^(k-1); 0; 0)
  all digits zero (n of them), a = 0:
        Ko: Conv -> Ke(0^b, 1, 0^(n-1); 0; 0)  (n >= 1),  Ke(0^b; 1; 0)  (n = 0)
        Ke: n = 0 halts (reached only from Ko(;0;0));    n = 1: Ko(; b+2; 0);   n >= 2: Ko(b+2, 0^(n-2); 0; 0)           (Final)
"""
import re, subprocess, sys

def step(par, ds, a, b):
    ds = list(ds)
    if a > 0:
        return par, ds, a - 1, b + 2
    nz = [i for i, d in enumerate(ds) if d]
    if nz:
        i = nz[-1]; k = len(ds) - 1 - i; y = ds[i] - 1
        if k == 0:
            return par, ds[:i] + [y], b + 2, 0
        return par, ds[:i] + [y, b + 2] + [0] * (k - 1), 0, 0
    n = len(ds)
    if par == 'o':
        if n == 0: return 'e', [0] * b, 1, 0
        return 'e', [0] * b + [1] + [0] * (n - 1), 0, 0
    if n == 0: return None
    if n == 1: return 'o', [], b + 2, 0
    return 'o', [b + 2] + [0] * (n - 2), 0, 0

def parse(line):
    m = re.match(r'(\d+) K([oe])\(([\d,]*); (\d+); (\d+)\)', line)
    if not m: return None
    return int(m.group(1)), m.group(2), [int(x) for x in m.group(3).split(',') if x != ''], int(m.group(4)), int(m.group(5))

if __name__ == '__main__':
    N = sys.argv[1]; maxp = sys.argv[2]
    out = subprocess.run(['./ksim.exe', 'run', N, maxp], capture_output=True, text=True).stdout.splitlines()
    ev = [parse(l) for l in out if parse(l)]
    print('literal events', len(ev), 'last step', ev[-1][0])
    # the abstract system also predicts how the literal visit sequence of K events continues; the literal run reports
    # every K event (both parities); the abstract one is stepped from the first event and compared event by event
    cur = ev[0][1:]
    bad = 0
    for i in range(1, len(ev)):
        nxt = step(cur[0], cur[1], cur[2], cur[3])
        lit = ev[i][1:]
        if nxt is None or (nxt[0], list(nxt[1]), nxt[2], nxt[3]) != (lit[0], lit[1], lit[2], lit[3]):
            print('MISMATCH at event', i, 'step', ev[i][0], 'abstract', nxt, 'literal', lit); bad += 1
            break
        cur = lit
    print('compared', len(ev) - 1, 'transitions, mismatches', bad)
    print('last literal event:', ev[-1][:2], 'len(ds)=%d' % len(ev[-1][2]), 'a=%d b=%d' % (ev[-1][3], ev[-1][4]))
