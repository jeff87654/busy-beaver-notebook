"""engpool.py: engchk + invchk on every h_*.tsv lacking .inv, 2 idle workers; then ana2 -> ana2.txt"""
import idle, glob, os, subprocess, sys, time
todo = [f for f in sorted(glob.glob('h_*.tsv')) if not os.path.exists(f + '.inv')]
run = []
def job(f):
    tag = os.path.basename(f)[2]
    pre = '' if os.path.exists(f + '.eng') and os.path.getmtime(f + '.eng') > os.path.getmtime(f) else f'"{sys.executable}" engchk.py {tag} {f} && '
    return subprocess.Popen(pre + f'"{sys.executable}" invchk.py {tag} {f}', shell=True, creationflags=0x40)
while todo or run:
    run = [p for p in run if p.poll() is None]
    while todo and len(run) < 2:
        f = todo.pop(0)
        if os.path.exists(f + '.inv'): continue
        run.append(job(f))
    time.sleep(3)
with open('ana2.txt', 'w') as fo: subprocess.run([sys.executable, 'ana2.py'], stdout=fo, creationflags=0x40)
open('notes.txt', 'a').write(time.strftime('%H:%M') + ' engpool done -> ana2.txt\n')
