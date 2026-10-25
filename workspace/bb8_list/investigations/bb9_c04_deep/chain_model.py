"""chain_model.py : the level-B cascade as a 5-adic affine chain, and heuristic entry statistics.
  step(L): r = L mod 5; r=1: (3L+32)/5, r=2: (3L-46)/5, r=3: (3L-64)/5, r=4: (3L-52)/5, r=0 (stop, L>=30): (3L-100)/5.
  All values are 1 mod 3.  Valid for L >= THR (empirically 60).  Below THR the TM's small-L endgame decides (table from survey).
Usage:
  python chain_model.py table SURVEYFILES...   : build key -> class table (key = first chain value < THR, or the start L0 if already < THR)
  python chain_model.py mc N [seed]            : Monte Carlo distribution of the entry key from random huge starts
  python chain_model.py path k                 : print the chain from an exhaustion start k (L0 = 3k-5)
"""
import sys, random, collections
THR = 60
C = {1: 32, 2: -46, 3: -64, 4: -52, 0: -100}

def step(L):
    r = L % 5
    if r == 0 and L < 30: return None          # not a valid stop: endgame
    return (3 * L + C[r]) // 5

def chain_to_window(L):
    """iterate until L < THR; returns (key, path)"""
    path = [L]
    while L >= THR:
        L = step(L); path.append(L)
    return L, path

def parse_survey(files):
    out = {}
    for f in files:
        for line in open(f):
            p = line.split()
            if len(p) < 3 or not p[0].isdigit(): continue
            k = int(p[0]); cls = p[1]
            if cls not in ('a', 'b', 'c'): continue
            out[k] = (cls, line.strip())
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'path':
        k = int(sys.argv[2]); key, path = chain_to_window(3 * k - 5); print('k=%d key=%d path=%s' % (k, key, path))
    elif cmd == 'table':
        sv = parse_survey(sys.argv[2:])
        tab = collections.defaultdict(set); src = collections.defaultdict(list)
        for k, (cls, line) in sorted(sv.items()):
            key, path = chain_to_window(3 * k - 5)
            tab[key].add(cls); src[key].append((k, cls, len(path) - 1))
        for key in sorted(tab):
            print('key %3d : %s  from k=%s' % (key, '/'.join(sorted(tab[key])), ' '.join('%d%s' % (k, c) for k, c, d in src[key])),
                  '' if len(tab[key]) == 1 else '   <<< INCONSISTENT')
    elif cmd == 'mc':
        N = int(sys.argv[2]); rnd = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        cnt = collections.Counter()
        for _ in range(N):
            L = rnd.randrange(10 ** 15, 10 ** 16); L += (1 - L) % 3
            key, path = chain_to_window(L); cnt[key] += 1
        for key in sorted(cnt): print(key, cnt[key], '%.4f' % (cnt[key] / N))
