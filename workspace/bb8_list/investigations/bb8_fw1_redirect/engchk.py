"""engchk.py TAG HFILE: for blank-engine-like leaves (status T) compare D/Bk outcomes with the base on 15 test configs
(kmap2 compare mode, stops at the first mismatch).  Writes HFILE.eng: machine, intact(1/0), #configs run."""
import idle, sys, subprocess, os
from bcfg import *
TAB, NL = chr(9), chr(10)
TESTS = [([3], 5), ([1, 2], 4), ([2, 3], 3), ([2, 0], 5), ([1, 1, 0], 4), ([2, 0, 0], 6), ([3, 0, 0], 5), ([2, 0, 0, 0], 7),
         ([1, 0, 0, 0, 0], 9), ([2, 1, 0], 6), ([1, 0, 2], 5), ([4, 2, 2], 3), ([3, 2, 2, 2, 1], 12), ([1, 3, 0, 0], 8), ([2, 2, 1, 0, 0, 0], 10)]
def main(tag, hf):
    M, tt, B0, fam = BASES[tag]; t = T(tag)
    sf = f'starts_chk_{tag}.txt'
    with open(sf, 'w') as f:
        for i, (ds, a) in enumerate(TESTS):
            w = word(tag, ds, a, B0); f.write(f"c{i} {w} {len(w)} {t['q']} 1" + NL)
    leaves = [l.split(TAB)[1] for l in open(hf) if not l.startswith('#') and l.split(TAB)[2][0] == 'T']
    mf = hf + '.mlist'; open(mf, 'w').write(NL.join([M] + leaves) + NL)
    p = subprocess.run([os.path.abspath('kmap2.exe'), mf] + targs(tag) + [sf, '20000', str(B0), 'cmp'], capture_output=True, text=True, creationflags=0x40)
    rows = [l.split(TAB) for l in p.stdout.splitlines()]
    with open(hf + '.eng', 'w') as f:
        for r in rows[1:]:
            f.write(r[0] + TAB + str(int(r[-1] == 'SAME')) + TAB + str(len(r) - 2) + NL)
    os.remove(mf)
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
