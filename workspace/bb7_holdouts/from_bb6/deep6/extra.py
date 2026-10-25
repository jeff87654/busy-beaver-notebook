"""extra.py SUFFIX: life (1e7 macro, K=2) for small-probe HALT rows -> life/K2<SUFFIX>.tsv (Idle)."""
import os, sys, subprocess, time, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import idle  # noqa
os.chdir(os.path.dirname(os.path.abspath(__file__))); suf = sys.argv[1]
ms = set()
for p in glob.glob('small/K*.tsv'):
    for l in open(p):
        f = l.split('\t')
        if len(f) > 2 and f[2] == 'HALT': ms.add(f[0])
done = set()
for p in glob.glob('life/K2*.tsv'):
    done |= {l.split('\t')[0] for l in open(p)}
ms = sorted(ms - done); os.makedirs('life', exist_ok=True)
open(f'life/K2{suf}.txt', 'w').write('\n'.join(ms) + '\n')
p = subprocess.Popen([os.path.abspath('../../nonlist/nlp7v.exe'), f'life/K2{suf}.txt', f'life/K2{suf}.tsv.tmp', '10000000', '--life', '--K=2'], creationflags=0x40)
open('../pids.txt', 'a').write(f"{time.strftime('%F %H:%M')} {p.pid} deep6 extra life K2{suf} ({len(ms)} rows)\n"); p.wait()
os.replace(f'life/K2{suf}.tsv.tmp', f'life/K2{suf}.tsv'); print('done', len(ms))
