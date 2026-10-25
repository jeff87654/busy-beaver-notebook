"""Check the family rules of the main machine against literal simulation for a given machine string.
usage: python rules_check.py TM"""
import sys, threading, os
threading.Timer(100, lambda: os._exit(3)).start()
import fam
from lit import parse
TMS = sys.argv[1]
fam.T = parse(TMS)
fam.TM = TMS
def nx_(a): return 6*a+40
cases = []
bad = 0
def chk(name, args, want):
    global bad
    got = fam.step_R(*args)
    ok = got is not None and got[0] == want
    print(('ok  ' if ok else 'BAD ') + name, args, 'want', want, 'got', got and got[0])
    if not ok: bad += 1
for m in range(0, 3):
    j = 3*m+2
    for a in (2, 3, 5):
        for ds in ((), (12,)):
            chk('N1', (j, a, ds), (j+3, a-1, ds))
    for d in (5, 9, 12):
        chk('N2+N3', (j, 1, (d,)), (j+20, d-4, ()))
    chk('N2p', (j, 1, (4,)), (1, 2*j+49, ()))
    chk('C1', (j, 1, (1,)), (j+16, 2, ()))
    chk('N2s', (j, 1, ()), (2, 2*j+37, ()))
for m in range(1, 4):
    J = 3*m+1
    for a in (5, 9, 13):
        chk('N3', (J, a, ()), (2, 2*J-3, (a-4,)))
for A in (13, 20):
    chk('N3p', (1, A, ()), (2, 14, (A-12,)))
for m in range(0, 3):
    J = 3*m+3
    chk('N3c0', (J, 2, ()), (2, 2*J+17, ()))
print('BAD count', bad)
