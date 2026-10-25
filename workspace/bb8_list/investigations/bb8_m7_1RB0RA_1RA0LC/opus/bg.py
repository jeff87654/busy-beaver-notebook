"""bg.py LOG cmd args... : start cmd at Idle priority, detached, stdout+stderr -> LOG; print the pid."""
import subprocess, sys
log = open(sys.argv[1], 'w')
p = subprocess.Popen(sys.argv[2:], stdout=log, stderr=subprocess.STDOUT,
                     creationflags=subprocess.IDLE_PRIORITY_CLASS | subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008)
open('pids.txt', 'a').write('%d %s\n' % (p.pid, ' '.join(sys.argv[2:])))
print(p.pid)
