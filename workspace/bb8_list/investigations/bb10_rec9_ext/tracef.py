"""Filtered hyb10 trace: canonical configs (state Q) printed when the item prefix (first N items, junk shortened)
changes.  Usage: python tracef.py MACHINE CONF MAXSTEPS [Q=A] [N=12] [W=230]"""
import subprocess, sys, re
m, conf, ms = sys.argv[1], sys.argv[2], sys.argv[3]
q = sys.argv[4] if len(sys.argv) > 4 else 'A'
N = int(sys.argv[5]) if len(sys.argv) > 5 else 12
W = int(sys.argv[6]) if len(sys.argv) > 6 else 230
H = '../bb10_bb7_descendants/hyb10.exe'
p = subprocess.Popen([H, m, conf, '0', 'I', ms, '-k', '100000000', '-m', '100000000', '-q', q, '-x'], stdout=subprocess.PIPE, text=True,
                     creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0))
prev = None
def short(it):
    it = re.sub(r'\(10\)\^\d+', '(10)^k', it)
    it = re.sub(r'^\d+\*\d+$', 'n*k', it)
    return it if not it.isdigit() else 'n'
for line in p.stdout:
    if not line.startswith(('C', 'H', 'T')):
        continue
    head, _, body = line.partition(' | ')
    items = body.split()
    key = tuple(items[:N])
    if key != prev or line[0] in 'HT':
        print(head.split()[1], ' '.join(items)[:W])
        prev = key
