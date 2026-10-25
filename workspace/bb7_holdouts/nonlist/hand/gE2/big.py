"""big.py MACRO SHOWN KS... : per machine x K, scan all show lines; report max #big runs (count>=T) in one snapshot,
the snapshot macro/steps where it occurs, and max #runs. Lines are tape tokens; (..)xN counted as one list token."""
import sys, subprocess, re, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
mm, sh, Ks, outf = sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4]
tags = sys.argv[5].split(',') if len(sys.argv) > 5 else None
T = 30
out = open(outf, 'w')
for line in open('list.tsv'):
    tag, m = line.split('\t')[:2]
    if tags and tag not in tags: continue
    fn = f'tmpb_{tag}.txt'; open(fn, 'w').write(m + '\n')
    for K in Ks:
        t0 = time.time()
        p = subprocess.Popen([D + r'\nlp7v.exe', fn, 'NUL', mm, '--life', '--K=' + K, '--show=' + sh], stdout=subprocess.PIPE, text=True, creationflags=0x40)
        open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE2\tnlp7v {tag} K{K}\n')
        best = (-1,); last = None; n = 0
        for l in p.stdout:
            if '|' not in l: continue
            n += 1
            head, tape = l.split('|', 1)
            tape = re.sub(r'\.\.\.', ' ', tape)
            ex = re.findall(r'\^(\d+)', re.sub(r'\([^)]*\)x\d+', ' ', tape))
            lists = [int(x) for x in re.findall(r'\)x(\d+)', tape)]
            big = [int(x) for x in ex if int(x) >= T] + [x for x in lists if x >= T]
            nb = len(big)
            if nb > best[0]: best = (nb, head.split()[0], head.split()[1], sorted(big)[-8:])
            last = (head.split()[0], head.split()[1], len(tape.split()))
        p.wait()
        out.write(f'{tag} K{K} lines={n} maxbig={best[0]} at macro {best[1]} steps {best[2]} vals {best[3]} | last {last} {time.time()-t0:.0f}s\n'); out.flush()
    import os; os.remove(fn)
