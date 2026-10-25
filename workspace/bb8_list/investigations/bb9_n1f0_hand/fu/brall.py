import sys
from backref import check
for line in open(sys.argv[1]):
    m = line.split()[0] if line.strip() else None
    if not m: continue
    r = check(m, 30)
    print(m, ' '.join('%s:%s' % (a, b.split()[0]) for a, b in r))
