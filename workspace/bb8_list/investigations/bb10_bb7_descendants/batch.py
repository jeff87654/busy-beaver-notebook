"""Run follow.py on every machine of a set file (MACHINE<TAB>tag), N workers, Idle priority.
   python batch.py SET.tsv RESULTS.tsv [WORKERS=6] [STAGES=6] [BUDGET=300000000]
Skips machines already in RESULTS.tsv.  Per-machine logs in logs/<machine>.log."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
import os
os.environ['HYBEXE'] = 'hyb10r.exe'
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
workers = int(sys.argv[3]) if len(sys.argv) > 3 else 6
stages = sys.argv[4] if len(sys.argv) > 4 else '6'
budget = sys.argv[5] if len(sys.argv) > 5 else '300000000'
rows = [l.split('\t') for l in src.read_text().splitlines() if l.strip()]
done = set()
if dst.exists():
    done = {l.split('\t')[0] for l in dst.read_text().splitlines()}
todo = [(r[0], r[1] if len(r) > 1 else '', r[2] if len(r) > 2 else '', r[3] if len(r) > 3 else '', r[4] if len(r) > 4 else '', r[5] if len(r) > 5 else '') for r in rows if r[0] not in done]
(HERE / 'logs').mkdir(exist_ok=True)
def job(mt):
    m, tag, tmpl, n, ref, blank = mt
    extra = (['--template', tmpl] if tmpl else []) + (['--n', n] if n else []) + (['--ref', ref] if ref else []) +             (['--blank'] if blank == 'blank' else [])
    log = HERE / 'logs' / f'{m}.log'
    try:
        r = subprocess.run([sys.executable, str(HERE / 'follow2.py'), m, '--stages', stages, '--budget', budget,
                            '--log', str(log), *extra], capture_output=True, text=True, creationflags=LOW, timeout=7200)
        res = [l for l in r.stdout.splitlines() if l.startswith('RESULT')]
        line = res[-1] if res else 'RESULT CRASH ' + (r.stderr.strip().splitlines() or ['?'])[-1]
    except subprocess.TimeoutExpired:
        line = 'RESULT WALLTIMEOUT'
    return m, tag, line
with ThreadPoolExecutor(workers) as ex, dst.open('a') as f:
    for fu in as_completed([ex.submit(job, t) for t in todo]):
        m, tag, line = fu.result()
        f.write(f'{m}\t{tag}\t{line}\n'); f.flush()
        print(m, tag, line[:200], flush=True)
