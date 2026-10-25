"""Follow the tail-exhaustion endings of a machine with rounds X(a,0,11111 r) -> X(2a+d, 0, r).
For a tail word w (the leftover after all 11111 blocks are used), run literally from X(a,0,w) for several a in the
counter's residue class and stop at the first later configuration X(A,0,r) (E0 at the left edge, blank left side,
word 1 (10)^A r, r = '' or starting with 1) that is either a reset (A = A0, r = 1^c w') or a completed counter
(A > a). The results are fitted as linear in a and the walk continues with the new tail."""
import sys, re
from ending import parse, M, VAR
from lit import Sim, compress

def run_to(tm, a, w, A0, maxsteps=10**7):
    s = Sim(tm, size=1 << 14)
    ww = [1] + [1, 0] * a + [int(x) for x in w]
    p = s.pos
    for i, x in enumerate(ww): s.tape[p + 1 + i] = x
    s.hi = p + len(ww); s.state = 4
    while s.steps < maxsteps:
        if not s.step():
            return ('HALT', s.steps)
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
            hi = s.hi
            while hi > s.pos and s.tape[hi] == 0: hi -= 1
            R = ''.join(map(str, s.tape[s.pos + 1:hi + 1]))
            A, B, r = parse(R)
            if B == 0 and (r == '' or r[0] == '1'):
                m = re.match(r'^(1*)(.*)$', r)
                c = len(m.group(1))
                if A == A0 and c >= a:
                    return ('RESET', s.steps, c, m.group(2))
                if A > a:
                    return ('COUNT', s.steps, A, r)
    return ('TIMEOUT',)

if __name__ == '__main__':
    which = sys.argv[1]
    tm = VAR if which == 'var' else M
    A0 = 3 if which == 'var' else 4
    res = int(sys.argv[2]); mod = int(sys.argv[3])   # counter a = res (mod mod)
    w = sys.argv[4] if len(sys.argv) > 4 else ''
    seen = []
    for it in range(30):
        As = [res + mod * j for j in (1, 2, 3, 4)]
        outs = [run_to(tm, a, w, A0) for a in As]
        kinds = set(o[0] for o in outs)
        print('tail %-20s a=%d mod %d:' % (w or 'e', res, mod), outs[:2])
        if kinds != {outs[0][0]} or outs[0][0] not in ('RESET', 'COUNT'):
            print('  non-uniform / halt'); break
        if outs[0][0] == 'RESET':
            cs = [o[2] for o in outs]; ws = set(o[3] for o in outs)
            d = [cs[i + 1] - cs[i] for i in range(3)]
            if len(set(d)) != 1 or len(ws) != 1 or d[0] % mod: print('  not linear', cs, ws); break
            slope = d[0] // mod; off = cs[0] - slope * As[0]
            wt = ws.pop()
            print('   RESET: X(a,0,%s) -> X(%d,0,1^(%d a + %d) %s)' % (w or 'e', A0, slope, off, wt))
            # new counter a = A0, rounds: tail 1^c wt, c = slope*a + off with a = res (mod mod)
            key = (w, res)
            if key in seen: print('  CYCLE closed'); break
            seen.append(key)
            # the next counter after rounds: a starts at A0; rounds map a -> 2a+dd; residue of a mod 5 at end
            # residue of c mod 5 determines the leftover
            cmod = (slope * res + off) % 5
            w = '1' * cmod + wt
            # the counter after the reset: A0, then rounds. Its residue mod (mod) is fixed by the round map
            res = int(sys.argv[5]) if len(sys.argv) > 5 else res
        else:
            As2 = [o[2] for o in outs]; rs = set(o[3] for o in outs)
            d = [As2[i + 1] - As2[i] for i in range(3)]
            print('   COUNT: A =', As2, 'tail', rs)
            if len(rs) != 1: print('  tails differ'); break
            slope = d[0] // mod; off = As2[0] - slope * As[0]
            key = (w, res)
            if key in seen: print('  CYCLE closed'); break
            seen.append(key)
            res = (slope * res + off) % mod
            w = rs.pop()
