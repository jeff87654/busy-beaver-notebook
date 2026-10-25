# acheck.py: residues of the affine power A(a,c,k,x) = a^k x + c (a^k-1)/(a-1) (symsim affPow) vs Python big integers
import subprocess, random, os, sys
EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1] if len(sys.argv) > 1 else 'symsim.exe')
random.seed(5); cases = []
for _ in range(400):
    a = random.randint(2, 7); c = random.randint(-5, 20); k = random.choice([random.randint(0, 300), random.randint(10**3, 10**18)]); x = random.randint(0, 10**6)
    if c < 0 and x * (a - 1) + c < 0: c = 0
    cases.append((a, c, k, x))
for M in (36, 720, 2520, 27720, 720720, 38918880):
    out = subprocess.run([EXE, 'wtab', '--mg', str(M)], input=''.join(f'A {a} {c} {k} {x}\n' for a, c, k, x in cases), capture_output=True, text=True).stdout.split('\n')
    got = [l.split() for l in out if l.startswith('A ')]
    bad = 0
    for (a, c, k, x), g in zip(cases, got):
        ak = pow(a, k, M * (a - 1)); e = (ak * x + c * ((ak - 1) // (a - 1))) % M
        if g[5] == 'UNDEC' or int(g[-1]) != e: bad += 1; print('MISMATCH', M, (a, c, k, x), g, e)
    print('M', M, 'cases', len(got), 'mismatches', bad)
