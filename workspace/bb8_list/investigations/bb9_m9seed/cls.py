# cls.py grade_output : classify m9s grade lines by their last jumps
import sys, collections
C = collections.defaultdict(list)
for l in open(sys.argv[1]):
    if not l.startswith('G '): continue
    head, tail = l.split('|')
    f = head.split(); out = f[3]; nj = int(f[6]); nrep = int(f[7])
    js = [t for t in tail.split()]
    jj = [int(t.split(':')[0]) for t in js]; bb = [t.split(':')[1] for t in js]
    if out == 'HALT':
        k = 'HALT-rep%d' % min(nrep, 9) if nrep else 'HALT-norep'
    elif nj == 0: k = out + '-nojump'
    elif nrep == 0: k = out + '-norep'
    elif len(jj) == 8 and len(set(bb)) == 1 and len(set(b - a for a, b in zip(jj, jj[1:]))) == 1 and jj[1] > jj[0]:
        k = out + '-LINJ'
    elif len(jj) == 8 and len(set(bb)) <= 2 and all(b >= a for a, b in zip(jj, jj[1:])):
        k = out + '-NEARLINJ'
    else: k = out + '-OTHER'
    C[k].append(l.rstrip())
for k in sorted(C): print(k, len(C[k]))
if len(sys.argv) > 2:
    for k in sys.argv[2].split(','):
        for l in C[k][:int(sys.argv[3]) if len(sys.argv) > 3 else 20]: print(l[:250])
