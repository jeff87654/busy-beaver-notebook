import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
from fit7 import Prober
rows = {l.split('\t')[0]: l.strip().split('\t') for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\mach.tsv') if l.strip()}
_, m, t = rows[sys.argv[1]]
P = Prober(m, t)
lists = eval(sys.argv[2]) if len(sys.argv) > 2 else [[], [1], [2], [3], [1, 0], [2, 0], [1, 1], [1, 0, 0], [2, 0, 0], [1, 0, 0, 0], [2, 1, 1, 1]]
def rl(ds):
    o=[];i=0
    while i<len(ds):
        j=i
        while j<len(ds) and ds[j]==ds[i]: j+=1
        o.append(str(ds[i])+('^%d'%(j-i) if j-i>1 else '')); i=j
    return ','.join(o) or '-'
for ds in lists:
    cf = [(ds, 0, a) for a in range(0, 16)]
    res = P.probe(cf, 300000000)
    out = []
    for (d, a, b), r in zip(cf, res):
        out.append('%d:%s' % (a, ('[%s;%d;%d]' % (rl(r[1]), r[2], r[3])) if r[0] == 'K' else r[0]))
    print(rl(ds), ' '.join(out)[:600], flush=True)
