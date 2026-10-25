"""launch.py NAME OUTFILE CMD... : start CMD detached (Idle priority is set by pkf itself), append the real PID to pids.txt.
Prints the PID.  Used so that every process can be killed by PID only."""
import subprocess, sys, os, time
name, out = sys.argv[1], sys.argv[2]; cmd = sys.argv[3:]
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists(cmd[0]): cmd[0] = os.path.abspath(cmd[0])
fo = open(out, 'w')
p = subprocess.Popen(cmd, stdout=fo, stderr=subprocess.STDOUT, creationflags=0x00000040)  # IDLE_PRIORITY_CLASS
open(os.path.join(base, 'pids.txt'), 'a').write('%d %s %s %s\n' % (p.pid, name, time.strftime('%H:%M:%S'), ' '.join(cmd)[:200]))
print(p.pid)
