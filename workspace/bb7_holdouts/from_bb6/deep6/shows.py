"""shows.py LIST OUT: last --show snapshot (1e7 macro) at the pilot K of each machine (Idle)."""
import os, sys, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import idle  # noqa
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pk = {}
for p in glob.glob('pil/*.tsv'):
    for l in open(p):
        f = l.split('\t')
        if len(f) > 1 and not l.startswith(('#', 'machine')): pk[f[0]] = f[1]
V = os.path.abspath('../../nonlist/nlp7v.exe')
with open(sys.argv[2], 'w') as o:
    for m in open(sys.argv[1]).read().split():
        open('show_tmp.txt', 'w').write(m + '\n')
        out = subprocess.run([V, 'show_tmp.txt', 'NUL', '10000000', '--life', f'--K={pk.get(m, "2")}', '--show=40'], capture_output=True, text=True, creationflags=0x40).stdout
        ls = [l for l in out.splitlines() if l.strip() and not l.startswith(('machine', '#'))]
        o.write(f'{m} K{pk.get(m)}\n  ' + '\n  '.join(x[:330] for x in ls[-3:]) + '\n'); o.flush()
