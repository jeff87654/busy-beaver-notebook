"""kv.py: run kview.exe at idle priority, record PID.  python kv.py ARGS..."""
import idle, subprocess, sys
from pathlib import Path
EXE = str(Path(__file__).resolve().parent / 'kview.exe')
p = subprocess.Popen([EXE] + sys.argv[1:], creationflags=0x40, stdout=subprocess.PIPE, text=True)
with open(Path(__file__).parent / 'pids.txt', 'a') as f: f.write(f'{p.pid} kview {" ".join(sys.argv[1:4])}\n')
out, _ = p.communicate(); sys.stdout.write(out)
