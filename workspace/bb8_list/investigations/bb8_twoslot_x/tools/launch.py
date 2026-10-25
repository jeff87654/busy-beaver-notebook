"""launch.py TAG -- cmd args... : start a detached process (stdout/stderr -> runs/TAG.log), record its Windows PID in pids.txt."""
import subprocess, sys, os, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tag = sys.argv[1]; cmd = sys.argv[3:] if sys.argv[2] == '--' else sys.argv[2:]
if not os.path.isabs(cmd[0]) and os.path.exists(os.path.join(BASE, cmd[0])): cmd[0] = os.path.join(BASE, cmd[0])
log = open(os.path.join(BASE, 'runs', tag + '.log'), 'w')
p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=BASE,
                     creationflags=0x00000200 | 0x00000040 | 0x08000000)  # DETACHED | NEW_PROCESS_GROUP | IDLE_PRIORITY
with open(os.path.join(BASE, 'pids.txt'), 'a') as f:
    f.write('%d %s %s %s\n' % (p.pid, time.strftime('%m-%d %H:%M:%S'), tag, ' '.join(cmd)[:200]))
print(p.pid)
