# postlit.py MACHINE TAPEFILE N1 N2 BUDGET : substitute X0=n into a symsim TAPE line and run lit from it
import sys, re, subprocess, os
D = os.path.dirname(os.path.abspath(__file__))
m, tf, n1, n2, bud = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
line = open(tf).read().split('\n')[0].split(' ', 1)[1]
specs = []
for n in range(n1, n2 + 1):
    s = re.sub(r'\{([^}]*)\}', lambda g: str(eval(g.group(1).replace('X0', str(n)))), line)
    specs.append(f'{m} A {s}\n')
out = subprocess.run([os.path.join(D, 'lit.exe'), bud], input=''.join(specs), capture_output=True, text=True).stdout
for n, l in zip(range(n1, n2 + 1), [x for x in out.split('\n') if x.startswith('L ')]): print(n, l.split()[3:])
