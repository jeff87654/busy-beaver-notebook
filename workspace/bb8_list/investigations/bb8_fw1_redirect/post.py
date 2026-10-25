"""post.py: wait for runall to finish, run engchk on every h file (idle), then ana2 -> ana2.txt"""
import idle, glob, os, time, subprocess, sys
jobs = [l.split() for l in open('jobs_all.txt') if l.strip()]
def fname(j): return f"h_{j[0]}_{j[1]}.tsv"
done = set()
while True:
    for j in jobs:
        fn = fname(j)
        if fn in done or not os.path.exists(fn): continue
        if '#summary' in open(fn).read()[-200:]:
            subprocess.run([sys.executable, 'engchk.py', j[0], fn], creationflags=0x40); done.add(fn)
    if len(done) == len(jobs): break
    time.sleep(20)
with open('ana2.txt', 'w') as f: subprocess.run([sys.executable, 'ana2.py'], stdout=f, creationflags=0x40)
open('notes.txt', 'a').write(time.strftime('%H:%M') + ' post.py: engchk + ana2 done -> ana2.txt\n')
