# ucheck.py: brute-force check of symsim's U residue law (BB(7)-champion engine) against big-integer arithmetic.
#  C(j,v,b) = iter v (U j) b with U_0(x) = 2^(2x+3) - 2, U_(j+1)(x) = iter (2x+2) (U_j) 0;  P(k,r) = 2^k (r+4) - 4.
import subprocess, sys, os
EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1] if len(sys.argv) > 1 else 'symsim.exe')
def U0(x): return 2 ** (2 * x + 3) - 2
def U0mod(x, M): return (pow(2, 2 * x + 3, M) - 2) % M
cases = []
for b in range(0, 300): cases.append(('C', 0, 1, b))                       # U_0(b)
for b in range(0, 8): cases.append(('C', 0, 2, b))                         # U_0(U_0(b))
cases += [('C', 1, 1, 0), ('C', 1, 1, 1), ('C', 0, 3, 0), ('C', 0, 4, 0), ('C', 2, 1, 0)]
for k in list(range(0, 200, 3)) + [10**6, 10**18 + 7]:
    for r in (1, 2, 5, 17, 10**25): cases.append(('P', k, r, None))
def expect(c, M):
    kind, a, b, x = c
    if kind == 'P': return (pow(2, a, M) * (b + 4) - 4) % M
    j, v = a, b
    if j == 0:
        y = x
        for _ in range(v - 1): y = U0(y)
        return U0mod(y, M)
    if (j, v, x) == (1, 1, 0): return 32766 % M
    if (j, v, x) == (1, 1, 1): return U0mod(U0(U0(6)), M)   # U_1(1) = U_0^4(0) = U_0(U_0(32766))
    if (j, v, x) == (2, 1, 0): return U0mod(U0(U0(6)), M)            # U_2(0) = U_1(U_1(0)) = U_1(32766) = U_0^65534(0): not computable
for M in (36, 720, 2520, 27720, 720720, 38918880):
    inp = ''.join(f'{k} {a} {b}' + (f' {x}' if x is not None else '') + '\n' for k, a, b, x in cases)
    out = subprocess.run([EXE, 'wtab', '--mg', str(M)], input=inp, capture_output=True, text=True).stdout.split('\n')
    got = {}
    for l in out:
        f = l.split()
        if l.startswith(('C ', 'P ')): got[(f[0], int(f[1]), int(f[2]), int(f[3]) if f[0] == 'C' else None)] = f[-1]
    bad = 0; n = 0
    for c in cases:
        if c == ('C', 2, 1, 0): continue
        e = expect(c, M); g = got.get(c)
        n += 1
        if g is None or g == 'UNDEC' or int(g) != e: bad += 1; print('MISMATCH', M, c, g, e)
    print('M', M, 'cases', n, 'mismatches', bad)
