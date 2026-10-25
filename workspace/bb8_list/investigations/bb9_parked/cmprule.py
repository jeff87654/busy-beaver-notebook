"""cmprule.py M1 M2 N SEED : random small Kt configs (far digits/tokens, m, r, t); run both machines literally (ktr.exe)
to the next K-moment and compare the token-level result.  Prints mismatches and a summary per config class."""
import random, subprocess, sys
m1, m2, N, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
MODE = sys.argv[5] if len(sys.argv) > 5 else "any"   # "g": digit form Kg only (tokens 3d+1, m = 3a+1, r = 3b+2)
rng = random.Random(seed)
def nxt(m, kt):
    o = subprocess.run(['./ktr.exe', m, '--kt', kt, '--nk', '1', '--maxs', '3e8'], capture_output=True, text=True).stdout.strip()
    if o.startswith('K'):
        tok = o.split('|')[1].strip(); rest = o.split('|')[2].split('used=')[0].strip()
        return tok + ' | ' + rest
    return o.split(' step')[0]
same = diff = 0
for i in range(N):
    nd = rng.randint(0, 5)
    ds = [3 * rng.choice([0, 0, 0, 1, 2, 3]) + 1 for _ in range(nd)] if MODE == "g" else [rng.choice([1, 1, 1, 4, 7, 10, 0, 2, 3, 5, 6]) for _ in range(nd)]
    ds = [0, 0] + ds                       # the far D0 D0 of the record family
    m = 3 * rng.randint(0, 4) + 1 if MODE == "g" else rng.choice([1, 4, 7, 3, 6, 2, 0, 5, 9, 10])
    r = (3 * rng.randint(0, 5) + 2) if MODE == "g" else rng.randint(0, 14); t = rng.randint(0, 3)
    kt = '%s;%d;%d;%d' % (','.join(map(str, ds)), m, r, t)
    a, b = nxt(m1, kt), nxt(m2, kt)
    if a == b: same += 1
    else:
        diff += 1; print('DIFF', kt, '\n   M1:', a, '\n   M2:', b)
print('same', same, 'diff', diff)
