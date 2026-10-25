import idle, sys, subprocess, re
# kn2.py "p1,q1;p2,q2;...;x,y" MAXMACRO [all]  : N2 segment-K follow
M = '1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA'
MS = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
segs = [tuple(map(int, s.split(','))) for s in sys.argv[1].split(';')]
toks = []
for i, (p, q) in enumerate(segs):
    if p: toks.append('01^%d' % p)
    if q: toks.append('10^%d' % q)
    if i < len(segs) - 1: toks.append('11^1')
init = 'A 0 | ' + ' '.join(toks) + ' [01]\n'
p = subprocess.Popen([MS, M, '2', sys.argv[2], 'r0', 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\pids.txt', 'a').write('%d ms kn2 %s\n' % (p.pid, sys.argv[1]))
p.stdin.write(init); p.stdin.close()
allk = len(sys.argv) > 3
last = None; n = 0
def parse(body):
    runs = re.findall(r'([01]{2})\^(\d+)', body)
    out = []; cur = [0, 0]; bad = []
    for b, c in runs:
        c = int(c)
        if b == '01': cur[0] += c
        elif b == '10': cur[1] += c
        elif b == '11' and c == 1: out.append(tuple(cur)); cur = [0, 0]
        else: bad.append(b + '^' + str(c))
    out.append(tuple(cur))
    return out, bad
for ln in p.stdout:
    if ln.startswith('H') or ln.startswith('END') or ln.startswith('IN'): print(ln.strip()); continue
    if ' A 0 |' not in ln or not ln.rstrip().endswith('[01]'): continue
    body = ln[ln.index('|') + 1:ln.rindex('[')]
    sg, bad = parse(body)
    key = (len(sg), tuple(sg[:-1]), tuple(bad))
    if allk or key != last:
        f = ln.split()
        print(f[2], 'segs=', ';'.join('%d,%d' % s for s in sg), ('BAD ' + ' '.join(bad)) if bad else '')
        n += 1
        if n > 200: p.kill(); break
    last = key
