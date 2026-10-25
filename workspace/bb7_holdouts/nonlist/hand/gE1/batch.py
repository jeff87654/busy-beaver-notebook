import sys, subprocess, os, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
rows = [l.split('\t') for l in open(D + r'\hand\groupE1_in.tsv') if l.strip()]
MM = sys.argv[1]; Ks = sys.argv[2].split(',')
out = open('batch_%s.txt' % MM, 'w')
for i, r in enumerate(rows, 1):
    m = r[0]; fn = 'm%02d.txt' % i; open(fn, 'w').write(m + '\n')
    for K in Ks:
        t = time.time()
        p = subprocess.Popen([D + r'\nlp7v.exe', fn, 'NUL', MM, '--life', '--K=' + K, '--show=40'], creationflags=0x40, stdout=subprocess.PIPE, text=True)
        open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE1\tnlp7v {K} {MM}\n')
        L = [l for l in p.stdout.read().splitlines() if '|' in l]; p.wait()
        last = L[-1] if L else 'NONE'
        out.write(f'#{i} K{K} {time.time()-t:.1f}s {last[:300]}\n'); out.flush()
