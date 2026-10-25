"""runall.py JOBFILE: run1.py jobs (lines 'TAG [SLOT]'), 2 idle workers."""
import idle, subprocess, sys, time
todo = [l.split() for l in open(sys.argv[1]) if l.strip()]
run = []
while todo or run:
    run = [p for p in run if p.poll() is None]
    while todo and len(run) < 2:
        j = todo.pop(0); p = subprocess.Popen([sys.executable, 'run1.py'] + j, creationflags=0x40)
        open('pids.txt', 'a').write(f"{p.pid} run1.py {' '.join(j)}\n"); run.append(p)
        open('notes.txt', 'a').write(f"{time.strftime('%H:%M')} start henum {' '.join(j)}\n")
    time.sleep(5)
open('notes.txt', 'a').write(f"{time.strftime('%H:%M')} runall {sys.argv[1]} done\n")
