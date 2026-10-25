import os, sys, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import idle  # noqa
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ms = sorted({l.split('\t')[0] for p in os.listdir('pil') if p.endswith('.tsv') for l in open('pil/' + p) if not l.startswith(('#', 'machine')) and l.split('\t')[1] == '6'})
open('small/K6.txt', 'w').write('\n'.join(ms) + '\n')
p = subprocess.Popen([os.path.abspath('../../nonlist/nlp7v.exe'), 'small/K6.txt', 'small/K6.tsv.tmp', '2000000', '--small', '--K=6'], creationflags=0x40)
open('../pids.txt', 'a').write(f"{time.strftime('%F %H:%M')} {p.pid} deep6 helper nlp7v small K6\n"); p.wait(); os.replace('small/K6.tsv.tmp', 'small/K6.tsv')
