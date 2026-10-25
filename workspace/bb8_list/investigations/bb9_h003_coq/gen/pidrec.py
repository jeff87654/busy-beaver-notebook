"""record this process's PID in bb9_h003_coq/pids.txt"""
import os, sys, time
from pathlib import Path
with open(Path(__file__).resolve().parents[1] / 'pids.txt', 'a') as f:
    f.write('%d gen %s %s\n' % (os.getpid(), ' '.join(sys.argv), time.strftime('%Y-%m-%d %H:%M:%S')))
