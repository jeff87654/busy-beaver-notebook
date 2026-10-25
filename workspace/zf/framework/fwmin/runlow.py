"""Run a command at IDLE priority (child inherits the priority class)."""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
import lowprio_local
out = open(sys.argv[1], 'w')
sys.exit(subprocess.call(sys.argv[2:], stdout=out))
