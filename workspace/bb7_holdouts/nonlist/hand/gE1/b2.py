import sys, subprocess, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
MM, SH, TL, W = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
for spec in sys.argv[5:]:
    i, K = spec.split(':'); fn = 'm%02d.txt' % int(i)
    p = subprocess.Popen([D + r'\nlp7v.exe', fn, 'NUL', MM, '--life', '--K=' + K, '--show=' + SH], creationflags=0x40, stdout=subprocess.PIPE, text=True)
    open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE1\tnlp7v {K} {MM}\n')
    L = [l for l in p.stdout.read().splitlines() if '|' in l]; p.wait()
    print(f'== #{i} K{K}')
    for l in L[-TL:]: print(l.strip()[:W])
