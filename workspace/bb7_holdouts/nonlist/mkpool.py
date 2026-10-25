"""mkpool.py: pool = pf7 PASS machines with no dlscan2 grade (dl2_out grade '-'), plus pf7 stats and dlscan2 n_templates.
Writes pool.tsv (machine span snaps maxblocks CS CSN RESETS halted ntmpl) and pool.txt (machines)."""
import glob, os, collections
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
out = open('pool.tsv', 'w'); outm = open('pool.txt', 'w')
out.write('machine\tspan\tsnaps\tmaxblocks\tCS\tCSN\tRESETS\thalted\tntmpl\n')
cnt = collections.Counter()
for pf in sorted(glob.glob(R + '/pf7_out/c*.tsv')):
    st = os.path.basename(pf)[:-4]
    dl = R + '/dl2_out/' + st + '.tsv'
    if not os.path.exists(dl): cnt['chunks_no_dl'] += 1; continue
    g = {}
    for l in open(dl):
        f = l.rstrip('\n').split('\t')
        if l.startswith(('#', 'machine')) or len(f) < 4: continue
        g[f[0]] = (f[3], f[2], f[1])
    for l in open(pf):
        f = l.rstrip('\n').split('\t')
        if len(f) < 11 or f[1] != 'PASS': continue
        cnt['pass'] += 1
        gr = g.get(f[0])
        if gr is None: gr = ('-', '?', '-1')
        if gr[0] != '-': cnt['graded'] += 1; continue
        if gr[2] != '-1': cnt['halted_in_dl2'] += 1
        cnt['pool'] += 1
        out.write('\t'.join([f[0], f[3], f[4], f[5], f[6], f[7], f[10], f[2], gr[1]]) + '\n'); outm.write(f[0] + '\n')
    cnt['chunks'] += 1
print(dict(cnt))
