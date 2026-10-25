"""1% random sample of the BB(7) holdouts through dlscan2 (census 300k, probes 20k), 2 Idle workers.
Writes sample1pct/s_{k}.txt (inputs) and sample1pct/s_{k}.tsv (outputs), hits -> sample1pct/hits.tsv."""
import idle, random, subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent; OUT = HERE / 'sample1pct'; EXE = HERE.parent / 'bb8_list' / 'neighbors' / 'dlscan2.exe'
if sys.argv[1:] == ['sample']:
    rng = random.Random(20261021); rows = []
    for c in sorted((HERE / 'chunks').glob('c*.txt')):
        rows += [l for l in open(c) if rng.random() < 0.01]
    for k in range(0, len(rows), 10000):
        (OUT / f's_{k//10000:02d}.txt').write_text(''.join(rows[k:k+10000]))
    print(len(rows), 'machines sampled')
else:
    def one(p):
        o = p.with_suffix('.tsv')
        if o.exists() and b'#summary' in open(o, 'rb').read()[-400:]: return
        subprocess.run([str(EXE), str(p), str(o), '300000', '20000'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=subprocess.IDLE_PRIORITY_CLASS)
        print(p.stem, flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, sorted(OUT.glob('s_*.txt'))))
    hits = [l for o in sorted(OUT.glob('s_*.tsv')) for l in open(o) if not l.startswith(('#', 'machine')) and l.split('\t')[3:4] not in ([], ['-'])]
    (OUT / 'hits.tsv').write_text(''.join(hits)); print('DONE hits:', len(hits))
