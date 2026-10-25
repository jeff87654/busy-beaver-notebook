# wcheck.py: brute-force check of symsim's W / iterated-W residue law against direct big-integer arithmetic.
#  W(2,b) = (3^(b+3)-5)/2 for b <= 400 and huge exact b (pow), W(3,1) = W2(119), W(3,2) = W(4,0) = W2(W2(119));
#  I(j,a,b) = iter a (W j) b:  I(1,a,b) = (3^a (2b+5) - 5)/2,  I(2,2,b) = W2(W2(b)),  I(2,3,0), I(2,4,0),
#  I(3,1,b) = W3(b) for b = 1, 2.
import subprocess, sys, random, os
EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1] if len(sys.argv) > 1 else 'symsim.exe')
def W2mod(b, M): return ((pow(3, b + 3, 2 * M) - 5) % (2 * M)) // 2
def W2(b): return (3 ** (b + 3) - 5) // 2
random.seed(1)
wcases = [(2, b) for b in list(range(0, 400)) + [random.randrange(10**18, 10**30) for _ in range(50)]]
w2_119 = W2(119)
icases = [(1, a, b) for a in range(0, 120, 7) for b in range(0, 40, 3)]
icases += [(2, 2, b) for b in range(0, 61)] + [(2, 3, 0), (2, 3, 1), (2, 4, 0), (3, 1, 1), (3, 1, 2), (3, 1, 0)]
t2 = W2(W2(0)); t3 = W2(t2)            # I(2,3,0) exact (1.1M digits)
t2b = W2(W2(1))
def iexp(j, a, b, M):
    if j == 1: return ((pow(3, a, 2 * M) * (2 * b + 5) - 5) % (2 * M)) // 2
    if (j, a) == (2, 2): return W2mod(W2(b), M)
    if (j, a, b) == (2, 3, 0): return W2mod(t2, M)
    if (j, a, b) == (2, 3, 1): return W2mod(t2b, M)
    if (j, a, b) == (2, 4, 0): return W2mod(t3, M)
    if (j, a, b) == (3, 1, 0): return 119 % M
    if (j, a, b) == (3, 1, 1): return W2mod(119, M)
    if (j, a, b) == (3, 1, 2): return W2mod(w2_119, M)
for M in (36, 720, 2520, 27720, 720720, 38918880):
    inp = ''.join(f'{j} {b}\n' for j, b in wcases) + '3 1\n3 2\n4 0\n' + ''.join(f'I {j} {a} {b}\n' for j, a, b in icases)
    out = subprocess.run([EXE, 'wtab', '--mg', str(M)], input=inp, capture_output=True, text=True).stdout.split('\n')
    got = {}; goti = {}
    for l in out:
        f = l.split()
        if l.startswith('W '): got[(int(f[1]), int(f[2]))] = int(f[5])
        if l.startswith('I '): goti[(int(f[1]), int(f[2]), int(f[3]))] = int(f[-1])
    bad = 0
    for j, b in wcases:
        if got[(j, b)] != W2mod(b, M): bad += 1; print('MISMATCH W', M, j, b)
    for (j, b), e in (((3, 1), W2mod(119, M)), ((3, 2), W2mod(w2_119, M)), ((4, 0), W2mod(w2_119, M))):
        if got[(j, b)] != e: bad += 1; print('MISMATCH W', M, j, b)
    for c in icases:
        if goti.get(c) != iexp(*c, M): bad += 1; print('MISMATCH I', M, c, goti.get(c), iexp(*c, M))
    print('M', M, 'W cases', len(wcases) + 3, 'I cases', len(icases), 'mismatches', bad)
