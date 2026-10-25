# compact.py FILE [maxw] : compact a drive.py output.  Consecutive J lines whose views have the same token count and differ
# only in at most 2 positions are folded: first line kept, then "... (n lines) ..." and the last line.
import sys, re
maxw = int(sys.argv[2]) if len(sys.argv) > 2 else 260
def toks(l):
    return l.partition('|')[2].split()
def similar(a, b):
    ta, tb = toks(a), toks(b)
    if len(ta) != len(tb): return False
    return sum(1 for x, y in zip(ta, tb) if x != y) <= 2
for name in sys.argv[1:2]:
    grp = []
    def flush():
        if not grp: return
        if len(grp) <= 3:
            for g in grp: print(g[:maxw])
        else:
            print(grp[0][:maxw]); print('   ... (%d similar) ...' % (len(grp) - 2)); print(grp[-1][:maxw])
        grp.clear()
    for line in open(name):
        line = line.rstrip('\n')
        if line.startswith('J'):
            if grp and not similar(grp[-1], line): flush()
            grp.append(line)
        else:
            flush(); print(line[:maxw])
    flush()
