"""Compare two gh_run logs stage by stage: same shapes? which tokens differ, and are the differences affine
(difference / step) with a common step.  usage: python cmp_logs.py A.log B.log STEP"""
import sys, re
def parse(fn):
    out = {}
    for l in open(fn):
        m = re.match(r'(\d+) (K|J): (.*)', l.rstrip('\n'))
        if not m: continue
        s, kind, body = int(m[1]), m[2], m[3]
        if kind == 'K':
            toks, _, rest = body.partition(' | a=')
            far = ''
            if ' far=' in rest:
                rest, far = rest.split(' far=')
            a, r = rest.split(' r=')
            out[(s, 'K')] = (toks.split(), int(a), int(r), far)
        else:
            m2 = re.match(r'ev=(\S+) zeros=(\d+) newr=(\S*) hd=(\S+) -> (.*) \| a=(\d+) r=(\d+)', body)
            out[(s, 'J')] = (m2[5].split(), int(m2[6]), int(m2[7]), m2[1])
    return out
def expand(toks):
    v = []
    for t in toks:
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v
A, B = parse(sys.argv[1]), parse(sys.argv[2]); step = int(sys.argv[3])
bad = 0
for key in sorted(A):
    if key not in B: print('missing in B', key); break
    ta, aa, ra, xa = A[key]; tb, ab, rb, xb = B[key]
    va, vb = expand(ta), expand(tb)
    if len(va) != len(vb):
        print(key, 'LENGTH', len(va), len(vb)); bad += 1; continue
    diffs = [(i, x, y) for i, (x, y) in enumerate(zip(va + [aa, ra], vb + [ab, rb])) if x != y]
    co = [(y - x) / step for _, x, y in diffs]
    nonint = [c for c in co if c != int(c)]
    if key[1] == 'K' and xa != xb and len(xa) != len(xb): print(key, 'FAR differs', len(xa), len(xb))
    if nonint: print(key, 'NON-AFFINE', diffs); bad += 1
    elif diffs: print(key, 'coef', ' '.join(f'{i}:{int(c)}' for (i, _, _), c in zip(diffs, co)))
print('stages compared', len(A), 'bad', bad)
