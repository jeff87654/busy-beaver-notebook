"""Screen looper variants.  python screen.py MACHINES.txt OUT.tsv MODE [WORKERS]
MODE c35: start must reproduce the BB(8) record run (list 4*34 1 at 3e6 steps); then K(0^35;0;b) (record template,
          canonical G) for b = 6, 7 to 5e7 steps: H / J (+ items) / T.
MODE rec: start must reach the BB(7) champion list (4*10 at 2e6 steps, canonical B); then K(0^11;0;b), b = 6, 7."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import follow2 as f
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
src, dst, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 3
EXE = str(HERE / 'hyb10r.exe')
TM = 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101'
def run(m, word, steps, start, canon):
    wf = HERE / 'loopvar' / 'tmpw' / (m.replace('-', 'x')[-40:] + f'_{len(word)}.txt')
    wf.parent.mkdir(exist_ok=True); wf.write_text(word or '0')
    r = subprocess.run([EXE, m, str(wf) if word else '-', str(len(word)), start, str(steps), '-q', canon],
                       capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
    return r[-1] if r else '?'
def job(m):
    if mode in ('c35', 'c35b'):
        if mode == 'c35':
            o = run(m, '', 3_000_000, 'A', 'P')
            if '| 4*34 1 ' not in o:
                return m, 'START-DIFFERS', ''
        res = []
        for b in (6, 7):
            w = f.word_of(f.inst(f.kword_sym(35, TM), {'b': b}))
            res.append(run(m, w, 50_000_000, 'G', 'G')[:200])
    else:
        if mode == 'rec':
            o = run(m, '', 2_000_000, 'A', 'B')
            if not o.startswith('J') or '| 0*2 4*10 ' not in o and '| 0*2 4*9 ' not in o:
                return m, 'START-DIFFERS', o[:80]
        res = []
        for b in (6, 7):
            w = f.word_of(f.inst(f.kword_sym(11), {'b': b}))
            res.append(run(m, w, 50_000_000, 'B', 'B')[:200])
    kinds = ''.join(x[0] for x in res)
    return m, 'EXH-' + kinds, ' || '.join(res)
done = {l.split('	')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
with ThreadPoolExecutor(W) as ex, dst.open('a') as out:
    for m, k, d in ex.map(job, [m for m in src.read_text().split() if m not in done]):
        out.write(f'{m}\t{k}\t{d}\n'); out.flush()
