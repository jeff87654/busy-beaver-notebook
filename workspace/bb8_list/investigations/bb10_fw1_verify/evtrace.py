"""literal trace of E0/I1/J0/J1 events (and the first B-form) from a B-form config.
   evtrace.py LIST:A [MAXEV]"""
import sys
from fw import *
from btrace import parse_list
_ts, A = sys.argv[1].rsplit(':', 1)
L = parse_list(_ts)
w, h, q = bword(L, int(A))
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 400
s = Server(M10, 'Bf,E0,I1,J0,J1', 10 ** 9)
for x in s.job(w, h, q, 10 ** 9):
    if x['kind'] == 'BF':
        p = bparse(x['word'], x['rel'])
        print('BF', x['step'], '[%s | %d]' % (fmt(p[0]), p[1]))
    else:
        print(show(x)[:400])
    mx -= 1
    if mx <= 0:
        break
s.close()
