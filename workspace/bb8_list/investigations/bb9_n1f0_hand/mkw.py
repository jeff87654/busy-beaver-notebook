"""print word for: J bo e1 e2,e3,e4 a b | K d1,..,dn a b | Kt ds m r t [pre] | T 'token view'"""
import sys
from c7lib import *
sys.path.insert(0, str(C7)); from tok2word import tok2word
def lst(s):
    out = []
    for x in s.split(','):
        if not x: continue
        if '*' in x: v, k = x.split('*'); out += [int(v)] * int(k)
        else: out.append(int(x))
    return out
k = sys.argv[1]
if k == 'J':
    print(J(int(sys.argv[2]), int(sys.argv[3]), [int(x) for x in sys.argv[4].split(',')], int(sys.argv[5]), int(sys.argv[6])))
elif k == 'K':
    print(K(lst(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
elif k == 'Kt':
    print(Kt(lst(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), *(sys.argv[6:7])))
else:
    print(tok2word(sys.argv[2]))
