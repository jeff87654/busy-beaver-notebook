import idle, subprocess, os, collections, time
from bcfg import *
rows = [l.rstrip('\n').split('\t') for l in open('noinv_leaves.txt')]
by = collections.defaultdict(list)
for r in rows: by[r[1]].append(r)
out = open('noinv_blank.tsv', 'w')
for tag, rs in by.items():
    fn = f'kb_noinv_{tag}.txt'; open(fn, 'w').write(''.join(r[0] + '\n' for r in rs))
    p = subprocess.Popen([os.path.abspath('kblank.exe'), fn] + targs(tag) + ['2000000', str(BASES[tag][2])], stdout=subprocess.PIPE, text=True, creationflags=0x40)
    open('pids.txt', 'a').write(f"{p.pid} kblank noinv {tag}\n")
    for l in p.stdout: out.write(tag + '\t' + l); out.flush()
    p.wait()
out.close(); open('notes.txt', 'a').write(time.strftime('%H:%M') + ' kblank on no-invariant K-like leaves done (noinv_blank.tsv)\n')
