import sys
from backref import check
for line in open(sys.argv[1]):
    m, c = line.split()
    print(m[28:], c, check(m, 80, 2000000))
