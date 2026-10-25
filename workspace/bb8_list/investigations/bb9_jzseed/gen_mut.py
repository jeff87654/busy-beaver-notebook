# gen_mut.py: all 1- and 2-slot changes of fw2 (champion labels, start E) and the champion (start A).
# Each slot ranges over the 36 defined values and '---' (halt).  Output: mut/in_<base>_<k>.txt  "MACHINE START"
import itertools
CH = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH'
FW = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RH0RA_1LB1LF_1RZ1RE_1LI1LI_0RE0LH'
VALS = [w + d + chr(65 + q) for w in '01' for d in 'LR' for q in range(9)] + ['---']
def slots(m): return [('---' if m[7*q+3*c+2] == 'Z' else m[7*q+3*c:7*q+3*c+3]) for q in range(9) for c in range(2)]
def join(sl): return '_'.join(sl[2*q] + sl[2*q+1] for q in range(9))
for name, base, st in (('fw2', FW, 'E'), ('champ', CH, 'A')):
    b = slots(base); seen = set()
    for k in (1, 2):
        out = open('mut/in_%s_%d.txt' % (name, k), 'w'); n = 0
        for pos in itertools.combinations(range(18), k):
            for vals in itertools.product(VALS, repeat=k):
                if any(v == b[p] for p, v in zip(pos, vals)): continue
                sl = list(b)
                for p, v in zip(pos, vals): sl[p] = v
                m = join(sl)
                if m in seen: continue
                seen.add(m); out.write('%s %s\n' % (m, st)); n += 1
        out.close(); print(name, k, n)
