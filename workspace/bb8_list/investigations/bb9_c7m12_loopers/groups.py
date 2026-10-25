"""groups.py: merge res_b6_*.tsv and res_b20_*.tsv into groups.tsv (one row per machine) and print a group table.
Behaviour signature: result kind, undefined slots read, cleared-list sequence pattern (first 6 entries), slope set."""
import glob, collections
def load(b):
    d = {}
    for fn in glob.glob(f'res_b{b}_*.tsv'):
        for l in open(fn):
            f = l.rstrip('\n').split('\t')
            if len(f) >= 11: d[f[0]] = f
    return d
r6, r20 = load(6), load(20)
grp = collections.defaultdict(list)
with open('groups.tsv', 'w') as fo:
    fo.write('machine\tgrade\tundefined\temu\tres_b6\thalt_b6\tundef_read_b6\tzeros_b6\tslopes_b6\tres_b20\thalt_b20\tundef_read_b20\tzeros_b20\tslopes_b20\n')
    for m, f in sorted(r6.items()):
        g = r20.get(m, [''] * 11)
        z6 = f[8].split(); z20 = g[8].split()
        sl = sorted(set(x.split(':')[1] for x in f[9].split()))
        sig = (f[4], f[7], ' '.join(z6[:6]), ','.join(sl), g[4], g[7], ' '.join(z20[:4]))
        grp[sig].append(m)
        fo.write('\t'.join([m, f[1], f[2], f[3], f[4], f[6], f[7], f[8], f[9], g[4], g[6], g[7], g[8], g[9]]) + '\n')
for i, (sig, ms) in enumerate(sorted(grp.items(), key=lambda x: -len(x[1]))):
    print(f'G{i+1}\tn={len(ms)}\tb6:{sig[0]} read={sig[1]} zeros=[{sig[2]} ..] slopes={sig[3]} | b20:{sig[4]} read={sig[5]} zeros=[{sig[6]} ..]')
    for m in ms[:3]: print('    ', m)
