import sys
from ksnap import run
n = int(sys.argv[1])
TOK = '100' * (n + 2) + '101'
for k in range(int(sys.argv[2]), int(sys.argv[3])):
    for x in (0,):
        right = '0' + '01' * x + '00' + '101' * k + TOK
        res = run('', 1, right, 3_000_000)
        print(k, res)
