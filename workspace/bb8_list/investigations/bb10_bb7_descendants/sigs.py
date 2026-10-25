"""Behaviour signatures: hash of the canonical-config item history from K(0^11;0;6) and K(0^11;0;7), 3e7 steps each.
   python sigs.py SET.tsv OUT.tsv [WORKERS]"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
src, dst = Path(sys.argv[1]), Path(sys.argv[2]); W = int(sys.argv[3]) if len(sys.argv) > 3 else 4
done = {l.split('\t')[0] for l in dst.read_text().splitlines()} if dst.exists() else set()
rows = [l.split('\t')[0] for l in src.read_text().splitlines() if l.strip()]
todo = [m for m in dict.fromkeys(rows) if m not in done]
def one(m, wf):
    w = (HERE / wf).read_text().strip()
    r = subprocess.run([str(HERE / 'hyb10h.exe'), m, str(HERE / wf), str(len(w)), 'B', '30000000', '-H', '-a', '1000000000'],
                       capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    h = r[0].split()[1] if r and r[0].startswith('HASH') else '?'
    last = r[-1] if r else '?'
    return h + ':' + last.split()[0]
def job(m):
    return m, one(m, 'wk6.txt') + '/' + one(m, 'wk7.txt')
with ThreadPoolExecutor(W) as ex, dst.open('a') as f:
    for m, s in ex.map(job, todo):
        f.write(f'{m}\t{s}\n'); f.flush()
