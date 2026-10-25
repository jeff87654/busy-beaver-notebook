"""collect.py: gather fitted dlscan3 rows of scans/n1f0/out/c_*.tsv (finished chunks only) into rows.tsv
(machine, grade, template, chunk, undefined slots).  Keeps every non-CHAMPION outer grade; CHAMPION rows go to
champ_rows.tsv (screened separately).  Prints the number of finished chunks and whether summary.txt exists."""
import glob, os
SC = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/nested_detector/scans/n1f0'
SL = [q + c for q in 'ABCDEFGHI' for c in '01']
KEEP = {'LOOPER', 'REBUILD', 'MULTI', 'MULTI?', 'R4-SOME', 'NOBOUNDARY', 'HALT?', 'HALT-SOME', 'CHECK'}
def undef(m):
    p = m.split('_')
    return ','.join(SL[2 * q + c] for q in range(len(p)) for c in range(2) if p[q][3 * c] == '-') or '-'
rows, champ, nfin = [], [], 0
for f in sorted(glob.glob(SC + '/out/c_*.tsv')):
    L = open(f).read().splitlines()
    if not any(l.startswith('#summary') for l in L):
        continue
    nfin += 1
    for l in L:
        if l.startswith('#') or l.startswith('machine'):
            continue
        x = l.split('\t')
        if len(x) < 5:
            continue
        r = [x[0], x[3], x[4], os.path.basename(f)[:-4], undef(x[0])]
        if x[3] in KEEP or x[3].startswith('W1-'):
            rows.append(r)
        elif x[3] == 'CHAMPION':
            champ.append(r)
open('rows.tsv', 'w').write(''.join('\t'.join(r) + '\n' for r in rows))
open('champ_rows.tsv', 'w').write(''.join('\t'.join(r) + '\n' for r in champ))
print(f'finished_chunks={nfin} rows={len(rows)} champion_rows={len(champ)} summary={os.path.exists(SC + "/summary.txt") or os.path.exists(SC + "/out/summary.txt")}')
