"""run.py LOG -- CMD...: run CMD at Idle priority, record its PID in pids.txt, wall time + stderr to LOG."""
import idle, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
i = sys.argv.index('--'); log = sys.argv[1]; cmd = sys.argv[i + 1:]
import os; cmd[0] = os.path.abspath(cmd[0])
env = None
t0 = time.time()
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(HERE / 'pids.txt', 'a') as f: f.write(f'{p.pid}\t{time.strftime("%Y-%m-%d %H:%M:%S")}\t{" ".join(cmd)}\n')
out, _ = p.communicate()
with open(log, 'a') as f: f.write(f'{" ".join(cmd)}\nrc={p.returncode} wall={time.time()-t0:.2f}s\n{out.decode(errors="replace")}\n')
