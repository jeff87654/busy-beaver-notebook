"""analyze.py: small-instance halting probe (nlp7s.exe --small) on the candidate families of cands.tsv, at K = 2, the
list K (SRK) and the pilot K. Writes ranked.tsv: class, verdict, machine, family size, SRs, FR, listcut, rounds, K.
  verdict SMALL-HALT : the small instance halts at some K (halt reachable at a forced exhaustion of the list)
          NO-HALT    : no halt within 2M macro steps at every K tried
Ranking: FR class first; SMALL-HALT before NO-HALT; then SRs (list length = depth proxy), then FR.
Runs at Idle priority, one process (pass W=2 for two)."""
import idle  # noqa: F401
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'nlp7s.exe')
W = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'cands.tsv')) if not l.startswith('class')]
byK = {}
for r in rows:
    for k in {'2', r[7], r[3]}:
        byK.setdefault(k, []).append(r[1])
os.makedirs(os.path.join(HERE, 'small'), exist_ok=True)
def run(k):
    inp = os.path.join(HERE, 'small', f'in_K{k}.txt'); out = os.path.join(HERE, 'small', f'out_K{k}.tsv')
    open(inp, 'w').write('\n'.join(byK[k]) + '\n')
    p = subprocess.Popen([EXE, inp, out, '2000000', '--small', f'--K={k}'], creationflags=0x40)
    open(os.path.join(HERE, 'pids.txt'), 'a').write(f'{p.pid}\tanalyze\tnlp7s.exe K{k}\n')
    p.wait(); return k
with ThreadPoolExecutor(W) as ex: list(ex.map(run, sorted(byK)))
res = {}
for k in byK:
    for l in open(os.path.join(HERE, 'small', f'out_K{k}.tsv')):
        f = l.rstrip('\n').split('\t')
        if f[0] == 'machine' or f[0].startswith('#') or len(f) < 7: continue
        cur = res.get(f[0])
        if cur is None or (f[2] == 'HALT' and cur[2] != 'HALT') or (f[2] == cur[2] and int(f[3]) > int(cur[3])):
            res[f[0]] = f
out = []
for r in rows:
    s = res.get(r[1], [r[1], '?', '?', '0', '0', '0', '0'])
    v = 'SMALL-HALT' if s[2] == 'HALT' else ('NO-HALT' if s[2] in ('-', 'LOOP') else '?')
    out.append((r[0], v, r[1], r[2], r[6], r[11], s[3], s[4], s[1], r[4], r[12][:120]))
out.sort(key=lambda x: (x[0] != 'FR', x[1] != 'SMALL-HALT', -int(x[4]), -int(x[5])))
with open(os.path.join(HERE, 'ranked.tsv'), 'w') as o:
    o.write('class\tverdict\tmachine\tfamily\tSRs\tFR\tlistcut\trounds\tK\tnat_lg\tshape\n')
    for x in out: o.write('\t'.join(map(str, x)) + '\n')
import collections
print(collections.Counter((x[0], x[1]) for x in out))
