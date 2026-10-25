"""chain.py WAITPID STEPFILE : wait until Windows PID WAITPID exits, then run the commands of STEPFILE one after the other
(one command per line, run from the bb9_redir dir; lines starting with # skipped).  Progress -> runs/chain.log."""
import subprocess, sys, os, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
waitpid, stepfile = sys.argv[1], sys.argv[2]
log = open(os.path.join(BASE, 'runs', 'chain.log'), 'a')
def alive(pid):
    r = subprocess.run(['tasklist', '/FI', 'PID eq %s' % pid, '/NH'], capture_output=True, text=True).stdout
    return pid in r
while waitpid != '0' and alive(waitpid): time.sleep(20)
for ln in open(os.path.join(BASE, stepfile)):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    log.write('%s START %s\n' % (time.strftime('%m-%d %H:%M:%S'), ln)); log.flush()
    p = subprocess.Popen(ln, shell=True, cwd=BASE)
    open(os.path.join(BASE, 'pids.txt'), 'a').write('%d chain-step %s %s\n' % (p.pid, time.strftime('%H:%M:%S'), ln[:120]))
    p.wait()
    log.write('%s DONE rc=%s %s\n' % (time.strftime('%m-%d %H:%M:%S'), p.returncode, ln)); log.flush()
log.write('%s CHAIN END\n' % time.strftime('%m-%d %H:%M:%S')); log.flush()
