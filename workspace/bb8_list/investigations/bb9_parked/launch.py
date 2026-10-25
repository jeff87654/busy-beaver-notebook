"""launch.py OUT TAG -- CMD... : start CMD detached at IDLE priority, stdout+stderr -> OUT, append 'PID TAG OUT CMD' to pids2.txt.
Kill only PIDs listed in pids2.txt (shared machine)."""
import subprocess, sys, os, time
here = os.path.dirname(os.path.abspath(__file__))
i = sys.argv.index('--')
out, tag = sys.argv[1], sys.argv[2]
cmd = sys.argv[i + 1:]
f = open(out, 'w')
IDLE = 0x40; DETACHED = 0x08; NEWGRP = 0x200
p = subprocess.Popen(cmd, cwd=here, stdout=f, stderr=subprocess.STDOUT, creationflags=IDLE | DETACHED | NEWGRP)
with open(os.path.join(here, 'pids2.txt'), 'a') as g:
    g.write('%d\t%s\t%s\t%s\t%s\n' % (p.pid, tag, time.strftime('%Y-%m-%d %H:%M:%S'), out, ' '.join(cmd)))
print(p.pid)
