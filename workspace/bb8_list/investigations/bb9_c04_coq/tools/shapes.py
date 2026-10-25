"""shapes.py: filter tokrle output; print a line only when its shape (numbers -> #, runs collapsed) is not among the
last W shapes (cycle-aware); report how many lines were skipped."""
import sys, re
W = int(sys.argv[1]) if len(sys.argv) > 1 else 8
def shape(s):
    s = re.sub(r'\^\d+', '', s)
    s = re.sub(r'\b\d{2,}\b', '#', s)
    out = []
    for w in s.split():
        if not out or out[-1] != w: out.append(w)
    return ' '.join(out)
win = []; skipped = 0; last = None
for line in sys.stdin:
    line = line.rstrip('\n')
    p = line.split(' ', 2)
    if len(p) < 3: continue
    sh = shape(p[2])
    if sh in win:
        skipped += 1; last = line
    else:
        if skipped: print('   ... %d skipped, last: %s' % (skipped, last[:300]))
        skipped = 0
        print(line[:400])
    if sh in win: win.remove(sh)
    win.append(sh); win = win[-W:]
if skipped: print('   ... %d skipped, last: %s' % (skipped, last[:300]))
