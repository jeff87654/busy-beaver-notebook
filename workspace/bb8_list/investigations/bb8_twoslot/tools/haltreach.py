"""haltreach.py TSV OUT : for every non-halting wtree/c231 row, decide whether any halt (undefined or lazy slot) can be read.
 static: halt slots of states reachable from A in the transition graph;  backref (bb8_resid backref_s, depth 40) on each.
 Classes: NOHALT_STATIC (no undefined slot in a reachable state), NOHALT_BACKREF (all reachable undefined slots
 UNREACHABLE by backward reasoning), POSSIBLE (some slot not refuted).  Writes OUT = TSV columns + class + slot detail."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bb8_resid', 'tools'))
import backref_s
TSV, OUT = sys.argv[1], sys.argv[2]
def slots(m): return [m[7 * q + 3 * b: 7 * q + 3 * b + 3] for q in range(len(m) // 7 + 1) for b in (0, 1)]
cache = {}
fo = open(OUT, 'w')
for l in open(TSV):
    p = l.rstrip('\n').split('\t')
    if p[2].startswith('HALT'): continue
    m = p[1].replace('zzz', '---')
    if m in cache: cls, det = cache[m]
    else:
        sl = slots(m); n = len(sl) // 2
        reach = {0}; stack = [0]
        while stack:
            q = stack.pop()
            for b in (0, 1):
                x = sl[2 * q + b]
                if '-' not in x:
                    t = ord(x[2]) - 65
                    if t < n and t not in reach: reach.add(t); stack.append(t)
        hs = [(q, b) for q in sorted(reach) for b in (0, 1) if '-' in sl[2 * q + b]]
        if not hs: cls, det = 'NOHALT_STATIC', ''
        else:
            res = backref_s.check(m, 40)
            # res: list of (slot, verdict) strings; keep only reachable states
            det = ' '.join(str(r) for r in res)
            hn = {'%s%d' % (chr(65 + q), b) for q, b in hs}
            poss = [r for r in res if r[0] in hn and not r[1].startswith('UNREACHABLE')]
            cls = 'POSSIBLE' if poss else 'NOHALT_BACKREF'
        cache[m] = (cls, det)
    fo.write('\t'.join(p[:3] + [cls, det[:200], p[8][:160]]) + '\n')
fo.close()
