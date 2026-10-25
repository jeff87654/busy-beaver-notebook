"""python fbatch.py MACHFILE OUT.tsv WORKERS STAGES BUDGET : fext --from-d2 on each machine (Idle), one RESULT line each
(results written as they complete; machines already in OUT are skipped)"""
import subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
LOW = subprocess.IDLE_PRIORITY_CLASS
HERE = Path(__file__).resolve().parent / 'fx'
src, out, W, ST, BUD = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
env = dict(os.environ, CLAUDE_JOB_DIR=r'C:/Users/jeffr/AppData/Local/Temp/claude/C--Users-jeffr-Downloads-bb8/08e94289-2f86-4acb-ab92-500b41a60e22/scratchpad')
ms = [l.split()[0] for l in Path(src).read_text().splitlines() if l.strip()]
done = {l.split('\t')[0] for l in out.read_text().splitlines()} if out.exists() else set()
ms = [m for m in ms if m not in done]
def job(m):
    try:
        lg = HERE / 'logs' / f'{m}.log'
        r = subprocess.run([sys.executable, 'fext.py', m, '--from-d2', '--stages', ST, '--budget', BUD, '--log', str(lg)],
                           cwd=HERE, capture_output=True, text=True, creationflags=LOW, env=env)
        res = [l for l in r.stdout.splitlines() if l.startswith('RESULT')]
        if not res:
            return m, 'NORESULT rc=%d %s' % (r.returncode, (r.stderr.strip().splitlines() or [''])[-1][:200])
        return m, res[-1]
    except Exception as ex:
        return m, f'NORESULT exception {type(ex).__name__}: {ex}'[:300]
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    for fu in as_completed([ex.submit(job, m) for m in ms]):
        m, res = fu.result()
        f.write(m + '\t' + res + '\n'); f.flush()
print('done', len(ms))
