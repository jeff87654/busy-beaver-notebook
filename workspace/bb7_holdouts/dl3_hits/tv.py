"""tv.py: run tview.exe at idle priority, record PID.  python tv.py ARGS..."""
import idle, subprocess, sys
from pathlib import Path
TV = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\tview.exe'
p = subprocess.Popen([TV] + sys.argv[1:], creationflags=0x40, stdout=subprocess.PIPE, text=True)
with open(Path(__file__).parent / 'pids.txt', 'a') as f: f.write(f'{p.pid} tview {" ".join(sys.argv[1:3])}\n')
out, _ = p.communicate(); sys.stdout.write(out)
