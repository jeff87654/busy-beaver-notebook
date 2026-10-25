from grid1 import nxt
bad=0; tot=0
for n in range(0, 13):
    for b in range(0, 10):
        got = nxt([0]*n, 0, b)
        exp = ([1]*n + [0]*(2*b+2), 1, 0)
        tot += 1
        if got[0] in ('HALT','TIMEOUT') or (got[1], got[2], got[3]) != exp:
            bad += 1; print('MISMATCH n=%d b=%d' % (n,b), 'got', got)
print('total', tot, 'bad', bad)
