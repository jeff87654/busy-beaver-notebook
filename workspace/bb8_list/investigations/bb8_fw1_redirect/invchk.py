"""invchk.py TAG HFILE: for engine-MODIFIED engine-like leaves, test mod-2 invariants Phi_x = x*a + sum(ds) (x=0,1)
under one K-step (random small configs, real K-moments b=B0).  Output HFILE.inv: machine, nK, ok0, ok1, Kfrac
(Kfrac = fraction of configs whose next event is a real K-moment; low = engine no longer list-like)."""
import idle, sys, subprocess, os, random
from bcfg import *
def ex(s):
    out = []
    for x in s.split(','):
        if not x: continue
        if '^' in x: v, n = x.split('^'); out += [int(v)] * int(n)
        else: out.append(int(x))
    return out
def main(tag, hf):
    M, tt, B0, fam = BASES[tag]; t = T(tag); random.seed(7)
    cf = []
    while len(cf) < 24:
        n = random.randint(1, 4); ds = [random.randint(1, 3)] + [random.choice([0, 1, 2, 3]) for _ in range(n - 1)]
        k = 0
        while k < len(ds) and ds[-1 - k] == 0: k += 1
        a = random.randint(k + 3, k + 8); cf.append((ds, a))
    sf = f'starts_inv_{tag}.txt'
    with open(sf, 'w') as f:
        for i, (ds, a) in enumerate(cf): w = word(tag, ds, a, B0); f.write(f"c{i} {w} {len(w)} {t['q']} 1\n")
    eng = {l.split('\t')[0]: l.split('\t')[1] for l in open(hf + '.eng')}
    leaves = [m for m, ok in eng.items() if ok == '0']
    if not leaves: open(hf + '.inv', 'w').close(); return
    TAB, NL = chr(9), chr(10)
    sf6 = f'starts_inv6_{tag}.txt'; open(sf6, 'w').write(''.join(open(sf).readlines()[:6]))
    mf = hf + '.ilist'; open(mf, 'w').write(NL.join(leaves) + NL)
    p = subprocess.run([os.path.abspath('kmap2.exe'), mf] + targs(tag) + [sf6, '20000', str(B0)], capture_output=True, text=True, creationflags=0x40)
    klike = [l.split(TAB)[0] for l in p.stdout.splitlines() if sum(x.startswith('K:') for x in l.split(TAB)[1:]) >= 3]
    nonk = [l.split(TAB)[0] for l in p.stdout.splitlines() if l.split(TAB)[0] not in set(klike)]
    open(mf, 'w').write(NL.join(klike) + NL)
    p = subprocess.run([os.path.abspath('kmap2.exe'), mf] + targs(tag) + [sf, '30000', str(B0)], capture_output=True, text=True, creationflags=0x40) if klike else None
    out = p.stdout.splitlines() if p else []
    out += [m + TAB + TAB.join(['T'] * len(cf)) for m in nonk]
    with open(hf + '.inv', 'w') as f:
        for l in out:
            r = l.split('\t'); m = r[0]; nK = 0; ok = [0, 0]
            for (ds, a), o in zip(cf, r[1:]):
                if not o.startswith('K:'): continue
                d2, a2, b2 = o[2:].split(';'); d2 = ex(d2); a2 = int(a2); nK += 1
                for x in (0, 1):
                    if (x * a + sum(ds)) % 2 == (x * a2 + sum(d2)) % 2: ok[x] += 1
            f.write(f"{m}\t{nK}\t{ok[0]}\t{ok[1]}\t{nK/len(cf):.2f}\n")
    os.remove(mf)
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
