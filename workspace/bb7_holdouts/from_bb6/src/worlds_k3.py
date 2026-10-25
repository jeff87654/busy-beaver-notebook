"""worlds_k3.py OUT: Kropitz 10^^15.6 machine: verify C(5)->C(35), C(7)->C((3^4+1)/2=41); halting worlds from C(4k)."""
import sys; sys.path.insert(0, '.')
from tm import parse, run
M = parse('1RB0LD_1RC0RF_1LC1LA_0LE1RZ_1LF0RB_0RC0RE')
def C(n): return '1' + '0' * n + '11' + '0' * 6, 1 + n + 2 + 5   # head on the 6th zero, state C
def nextC(n, maxs=10**8):
    tape, pos = C(n); found = []
    def stop(T, p, q, t, lo, hi, off):
        if t > 0 and q == "C" and T[p] == 0 and all(T[i] == 0 for i in range(p, hi + 1)):
            b = p - 1
            while b > lo and T[b] == 0: b -= 1
            if p - b != 6 or T[b] != 1 or T[b-1] != 1: return False
            a = lo
            while T[a] == 0: a += 1
            s = ''.join(map(str, T[a:b+1]))
            if s[0] == '1' and set(s[1:-2]) <= {'0'}: found.append(len(s) - 3); return True
        return False
    r = run(M, tape, pos, 'C', maxs, stop)
    return r[0], r[1], (found[0] if found else None), r
if __name__ == '__main__':
    for n in (5, 7, 6, 9):
        st, t, nn, r = nextC(n); print('C(%d) ->' % n, st, t, 'C(%s)' % nn, file=sys.stderr)
    out = []
    for k in range(1, 61):
        st, t, nn, r = nextC(4 * k)
        if st != 'HALT': print('C(%d) no halt' % (4*k), st, file=sys.stderr); continue
        _, t, T, p, q, lo, hi, off = r
        lo = min(lo, p) - 2; hi = max(hi, p) + 2
        out.append(f"W k3_C{4*k} {''.join(map(str, T[lo:hi+1]))} {p-lo} {q}")
        if k <= 2: print('C(%d) halts after %d at %s%d' % (4*k, t, q, T[p]), file=sys.stderr)
    open(sys.argv[1], 'w').write('\n'.join(out) + '\n'); print(len(out), 'worlds', file=sys.stderr)
