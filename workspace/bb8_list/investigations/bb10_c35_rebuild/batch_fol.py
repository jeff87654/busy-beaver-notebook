"""Run follow2.py (local copy, local hyb10.exe) on every machine of a set file (MACHINE[<TAB>tag[<TAB>ref]]) from the
BB(8) record's exhaustion K(0^35; 0; B) (template of the record), N workers, Idle priority.
   python batch_fol.py SET.tsv RESULTS.tsv [WORKERS=4] [STAGES=10] [BUDGET=100000000] [WALL=3600]
Skips machines already in RESULTS.tsv.  Per-machine logs in logs/<machine>.log."""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
TMPL = 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101'
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
stages = sys.argv[4] if len(sys.argv) > 4 else '10'
budget = sys.argv[5] if len(sys.argv) > 5 else '100000000'
wall = int(sys.argv[6]) if len(sys.argv) > 6 else 3600
rows = [l.rstrip('\n').split('\t') for l in src.read_text().splitlines() if l.strip()]
done = set()
if dst.exists():
    done = {l.split('\t')[0] for l in dst.read_text().splitlines()}
todo = [(r[0], r[1] if len(r) > 1 else '', r[2] if len(r) > 2 else '') for r in rows if r[0] not in done]
(HERE / 'logs').mkdir(exist_ok=True)
def job(t):
    m, tag, ref = t
    extra = ['--ref', ref] if ref else []
    log = HERE / 'logs' / f'{m}.log'
    try:
        r = subprocess.run([sys.executable, str(HERE / 'follow2.py'), m, '--template', TMPL, '--n', '35', '--stages', stages,
                            '--budget', budget, '--log', str(log), *extra], capture_output=True, text=True,
                           creationflags=LOW, timeout=wall, cwd=str(HERE))
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
