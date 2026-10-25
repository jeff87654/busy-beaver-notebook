"""tri.py MACRO KS: for each machine in list.tsv, nlp7v --show at each K, keep last shown line (trunc)."""
import sys, subprocess, os, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
mm = sys.argv[1]; Ks = sys.argv[2].split(','); out = open(sys.argv[3], 'w')
for line in open('list.tsv'):
    tag, m = line.split('\t')[:2]
    fn = f'tmp_{tag}.txt'; open(fn, 'w').write(m + '\n')
    for K in Ks:
        t = time.time()
        p = subprocess.Popen([D + r'\nlp7v.exe', fn, 'NUL', mm, '--life', '--K=' + K, '--show=6'], stdout=subprocess.PIPE, text=True, creationflags=0x40)
        open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE2\tnlp7v {tag} K{K}\n')
        o = p.communicate()[0].strip().splitlines()
        last = [l for l in o if '|' in l][-2:]
        out.write(f'{tag} K{K} {time.time()-t:.0f}s\n')
        for l in last: out.write('   ' + l[:260] + '\n')
        out.flush()
    os.remove(fn)
