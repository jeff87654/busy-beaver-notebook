# launch.py OUT CMD... : start detached at Idle priority (wsim sets it itself), record the real PID
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]; cmd = sys.argv[2:]
if not os.path.isabs(cmd[0]): cmd[0] = os.path.join(HERE, cmd[0])
f = open(os.path.join(HERE, out), "w")
p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=HERE, creationflags=0x00000008 | 0x00000200)
open(os.path.join(HERE, "pids.txt"), "a").write(f"{p.pid} {os.path.basename(cmd[0])} {out}\n")
print(p.pid)
