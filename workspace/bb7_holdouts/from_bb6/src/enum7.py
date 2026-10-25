"""enum7.py BASE SLOT [--both-free]: extensions of BASE (n states) with SLOT (e.g. B1) -> {0,1}{L,R}NEW and a new state
NEW = chr(65+n); NEW0, NEW1 each = halt or {0,1}{L,R}{A..NEW}; at least one halt (both-halt row included).
Prints one machine per line (TNF-irrelevant: NEW is only reachable through SLOT, so no duplicates)."""
import sys
def ext(base, slot):
    rows = base.split('_'); n = len(rows); new = chr(65 + n)
    q, c = ord(slot[0]) - 65, int(slot[1])
    opts = [f"{w}{d}{chr(65 + t)}" for w in '01' for d in 'LR' for t in range(n + 1)]
    out = []
    for red in [f"{w}{d}{new}" for w in '01' for d in 'LR']:
        r = list(rows); s = r[q]; r[q] = (red + s[3:]) if c == 0 else (s[:3] + red)
        for g0 in ['---'] + opts:
            for g1 in ['---'] + opts:
                if g0 != '---' and g1 != '---': continue
                out.append('_'.join(r + [g0 + g1]))
    return out
if __name__ == '__main__':
    for m in ext(sys.argv[1], sys.argv[2]): print(m)
