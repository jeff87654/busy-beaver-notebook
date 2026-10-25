"""idle.py OUT -- CMD ARGS... : run CMD at IDLE priority with stdout -> OUT (stderr -> OUT.err), detached."""
import subprocess, sys
out = sys.argv[1]; cmd = sys.argv[3:]
subprocess.Popen(cmd, stdout=open(out, 'w'), stderr=open(out + '.err', 'w'),
                 creationflags=subprocess.IDLE_PRIORITY_CLASS | subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
