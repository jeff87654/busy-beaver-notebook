# Verify R1-R3 of the list family by literal simulation (gparse.exe) on constructed configurations.
# C(ds | b) = 1 ((10)^(2d+1) 1)... ((10)^(2b+1) 1) G>   (far end first; head on the blank right of the word)
import subprocess, sys, itertools, random
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC'
def word(ds, b):
    return '1' + ''.join('10'*(2*d+1) + '1' for d in list(ds)+[b])
def nxt(ds, b, maxsteps=10**8, nev=1, m=M):
    w = word(ds, b)
    out = subprocess.run(['./gparse.exe', m, str(maxsteps), w, str(len(w)), 'G', '1', str(nev)], capture_output=True, text=True).stdout.strip().split('\n')
    res = []
    for line in out:
        p = line.split()
        if p[0] in ('HALT', 'END'): res.append(tuple(p)); break
        if p[2] == 'PARSEFAIL': res.append(('PARSEFAIL', p[0], p[4][:200])); break
        ns = list(map(int, p[4:]))
        if any(x % 2 == 0 for x in ns): res.append(('EVEN', p[0], ns)); break
        res.append((int(p[0]), [(x-1)//2 for x in ns[:-1]], (ns[-1]-1)//2))
    return res
def rule(ds, b):
    ds = list(ds)
    if ds and ds[-1] > 0: return ds[:-1] + [ds[-1]-1], b+2
    j = max((i for i, d in enumerate(ds) if d > 0), default=None)
    if j is None: return None
    k = len(ds) - j - 2   # zeros after position j+1
    return ds[:j] + [ds[j]-1, b+2] + [0]*k, 0
if __name__ == '__main__':
    random.seed(1)
    bad = 0; n = 0
    cases = []
    for m in range(1, 6):
        for ds in itertools.product(range(4), repeat=m):
            for b in (0, 1, 2, 5, 9):
                cases.append((ds, b))
    for _ in range(300):
        m = random.randint(1, 12)
        ds = [random.choice([0,0,0,1,2,3,7,20]) for _ in range(m)]
        cases.append((ds, random.choice([0,1,3,10,40,101])))
    for ds, b in cases:
        exp = rule(ds, b)
        if exp is None: continue
        r = nxt(ds, b)
        n += 1
        if not r or r[0][0] in ('HALT','END','PARSEFAIL','EVEN') or (r[0][1], r[0][2]) != (exp[0], exp[1]):
            bad += 1
            if bad < 20: print('MISMATCH', ds, b, 'expected', exp, 'got', r)
    print('checked', n, 'bad', bad)
