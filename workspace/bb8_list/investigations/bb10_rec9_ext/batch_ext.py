"""Run fext.py on every machine of a list (MACHINE[<TAB>tag]), N workers, Idle priority, skipping done ones.
   python batch_ext.py LIST RESULTS.tsv [WORKERS=3] [STAGES=40]
Per-machine logs: logs/fext_<machine>.log"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
stages = sys.argv[4] if len(sys.argv) > 4 else '40'
extra = sys.argv[5:]          # e.g. --budget 2000000000 --no-retry
rows = [l.split('\t') for l in src.read_text().splitlines() if l.strip()]
done = set()
if dst.exists():
    done = {l.split('\t')[0] for l in dst.read_text().splitlines()}
todo = [(r[0], r[1] if len(r) > 1 else '') for r in rows if r[0] not in done]
(HERE / 'logs').mkdir(exist_ok=True)


def job(mt):
    m, tag = mt
    log = HERE / 'logs' / f'fext_{m}.log'
    try:
        r = subprocess.run([sys.executable, str(HERE / 'fext.py'), m, '--stages', stages, '--log', str(log), *extra],
                           capture_output=True, text=True, creationflags=LOW, timeout=4 * 3600)
        res = [l for l in r.stdout.splitlines() if l.startswith('RESULT')]
        line = res[-1] if res else 'RESULT CRASH ' + (r.stderr.strip().splitlines() or ['?'])[-1]
    except subprocess.TimeoutExpired:
        line = 'RESULT WALLTIMEOUT'
    return m, tag, line


with ThreadPoolExecutor(workers) as ex, dst.open('a') as f:
    for fu in as_completed([ex.submit(job, t) for t in todo]):
        m, tag, line = fu.result()
        f.write(f'{m}\t{tag}\t{line}\n')
        f.flush()
        print(m, tag, line[:200], flush=True)
