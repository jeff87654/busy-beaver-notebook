"""deep.py: deep scan of the 22,089-row 6-state pool (22,069 embedded holdouts + 20 halt-undefined top-list controls).
Two Idle lanes, resumable per 2000-row chunk (ch/pNN.txt):
  lane A: dlscan2 (census 2e7, probes 2e4, --all; templates column stripped) -> dl2/pNN.tsv ; dlscan (census 2e7, probes 1e5) -> dl/pNN.tsv
  lane B: nlp7 --pilotonly -> pil/pNN.tsv ; nlp7f 1e7 macro --k2 (10x the BB(7) scan) on ALL rows -> full/pNN.tsv
A file is done when it contains '#summary'."""
import os, sys, subprocess, threading, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idle  # noqa
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
NB = os.path.abspath(os.path.join(H, '..', '..', '..', 'bb8_list', 'neighbors')); NL = os.path.abspath(os.path.join(H, '..', '..', 'nonlist'))
PIDS = os.path.join(H, '..', 'pids.txt'); lock = threading.Lock()
def done(p): return os.path.exists(p) and b'#summary' in open(p, 'rb').read()[-400:]
def run(cmd, out, strip=False):
    if done(out): return
    tmp = out + '.tmp'; args = [a.replace('@OUT', tmp) for a in cmd]
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x40)
    with lock, open(PIDS, 'a') as f: f.write(f"{time.strftime('%F %H:%M')} {p.pid} deep6 {os.path.basename(args[0])} {os.path.basename(out)}\n")
    p.wait()
    if strip:
        with open(tmp) as fi, open(out, 'w') as fo:
            for l in fi: fo.write('\t'.join(l.rstrip('\n').split('\t')[:6]) + '\n')
        os.remove(tmp)
    else: os.replace(tmp, out)
chunks = sorted(f[:-4] for f in os.listdir('ch') if f.endswith('.txt'))
for d in ('dl2', 'dl', 'pil', 'full'): os.makedirs(d, exist_ok=True)
def laneA():
    for c in chunks: run([os.path.join(NB, 'dlscan2.exe'), f'ch/{c}.txt', '@OUT', '20000000', '20000', '--all'], f'dl2/{c}.tsv', strip=True)
    for c in chunks: run([os.path.join(NB, 'dlscan.exe'), f'ch/{c}.txt', '@OUT', '20000000', '100000'], f'dl/{c}.tsv')
def laneB():
    for c in chunks: run([os.path.join(NL, 'nlp7.exe'), f'ch/{c}.txt', '@OUT', '--pilotonly'], f'pil/{c}.tsv')
    for c in chunks: run([os.path.join(NL, 'nlp7f.exe'), f'ch/{c}.txt', '@OUT', '10000000', '--k2'], f'full/{c}.tsv')
ta, tb = threading.Thread(target=laneA), threading.Thread(target=laneB); ta.start(); tb.start(); ta.join(); tb.join()
print('deep.py done', flush=True)
