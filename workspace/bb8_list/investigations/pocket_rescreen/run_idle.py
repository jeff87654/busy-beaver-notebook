"""run_idle.py LOG CMD...: run CMD at Idle priority (inherited), record own PID + child PID in pids.txt."""
import idle, subprocess, sys, os, time
log = sys.argv[1]; cmd = sys.argv[2:]
with open(log, 'w') as lf:
    p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pids.txt'), 'a') as f:
        f.write('%s wrapper=%d child=%d %s\n' % (time.strftime('%F %T'), os.getpid(), p.pid, ' '.join(cmd)[:200]))
    sys.exit(p.wait())
