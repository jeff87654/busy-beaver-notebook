import idle, sys, subprocess
# ff.py ID "ds a b" N MAXOUT : ffree summary (P' shortened to length + head)
FF = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\ffree.exe'
rows = {l.split('\t')[0]: l.strip().split('\t') for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\mach.tsv') if l.strip()}
_, m, t = rows[sys.argv[1]]
f = t.split(','); d = {}
for x in f[2:]:
    k, v = x.split('=', 1); d[k] = v
al, be = d['d'].split('d+'); aB, bB = d['b'].split('b+')
args = [FF, m, f[0], f[1], d['P'], d['u'], d['s'], al, be, aB, bB, d['S'], sys.argv[3], sys.argv[4]]
p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\pids.txt', 'a').write('%d ffree %s %s\n' % (p.pid, sys.argv[1], sys.argv[2]))
out, _ = p.communicate(sys.argv[2] + '\n')
for ln in out.splitlines():
    fs = ln.split()
    if fs[0] == 'K':
        P = fs[2][2:]
        toks = P.split('.')
        Ps = P if len(P) < 40 else '%s..(%d toks)..%s' % ('.'.join(toks[:4]), len(toks), '.'.join(toks[-5:]))
        print(fs[1], 'P=' + Ps, ' '.join(fs[3:])[:150])
    else: print(ln[:150])
