"""collect.py: summarise full_out/*.tsv (nlp7f rows) -> cands.tsv (ranked) + summary on stdout.

FAST  = natural run at the pilot K reaches >= 1e9.8 base steps in 1M macro steps (calibration: every rank7 row of level
        >= 3 has 10.1-10.8, every slow row <= 7.2), or the K=2 run reaches it.
FR    = value of a slowly decrementing digit next to a list (refilled digit; > 0 only for f_omega-class rows in the
        calibration set: champion 11, champ_231 22, level-16..424 rows 43-44; 0 for level <= 7 rows).
SRs   = length of the stable list of equal digits (champion 5, champ_231 18, level-47 row 22, level-424 rows 210).
Families: rows with identical (nat_lg, maxcnt, SRs, SRend, FR, k2_lg) are grouped; the first machine represents them.
Ranking: FR > 0 first, by SRs then FR; then FAST rows with SRs >= 10 (no refilled digit seen) by SRs.
"""
import glob, os, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FDIR = sys.argv[1] if len(sys.argv) > 1 else 'full_out'
COUT = sys.argv[2] if len(sys.argv) > 2 else 'cands.tsv'
HOUT = sys.argv[3] if len(sys.argv) > 3 else 'halts.tsv'
rows = []; nfile = 0; nmach = 0
for p in sorted(glob.glob(os.path.join(HERE, FDIR, '*.tsv'))):
    nfile += 1
    for l in open(p):
        if l.startswith(('#', 'machine')): continue
        f = l.rstrip('\n').split('\t')
        if len(f) < 18: continue
        nmach += 1
        rows.append(f)
def fl(x):
    try: return float(x)
    except ValueError: return 0.0
fast = [f for f in rows if fl(f[3]) >= 9.8 or (fl(f[11]) >= 9.8 and f[11] != '99.00')]
halts = [f for f in rows if f[2] == 'HALT' or f[15] == 'HALT']
fam = collections.OrderedDict()
for f in fast:
    key = (f[3], f[4], f[6], f[9], f[16], f[11])
    fam.setdefault(key, []).append(f)
c1 = [(v[0], len(v)) for v in fam.values() if int(v[0][16]) > 0]
c2 = [(v[0], len(v)) for v in fam.values() if int(v[0][16]) == 0 and int(v[0][6]) >= 10]
c1.sort(key=lambda x: (-int(x[0][6]), -int(x[0][16])))
c2.sort(key=lambda x: -int(x[0][6]))
with open(os.path.join(HERE, COUT), 'w') as o:
    o.write('class\tmachine\tfamily_size\tK\tnat_lg\tmaxcnt\tSRs\tSRK\tSRend\tSRsit_lg\tk2_lg\tFR\tshape\n')
    for cls, lst in (('FR', c1), ('SR', c2)):
        for f, n in lst:
            o.write('\t'.join([cls, f[0], str(n), f[1], f[3], f[4], f[6], f[8], f[9], f[10], f[11], f[16], f[17][:200]]) + '\n')
print(f'files {nfile}, machines {nmach}, FAST {len(fast)} ({len(fam)} families), HALT rows {len(halts)}')
print(f'FR>0 families {len(c1)} (machines {sum(n for _, n in c1)}); FAST SRs>=10 no-FR families {len(c2)}')
for f, n in c1[:15]: print('FR', f[0], n, 'SRs', f[6], 'FR', f[16], 'nat', f[3])
if halts:
    with open(os.path.join(HERE, HOUT), 'w') as o:
        for f in halts: o.write('\t'.join(f[:17]) + '\n')
