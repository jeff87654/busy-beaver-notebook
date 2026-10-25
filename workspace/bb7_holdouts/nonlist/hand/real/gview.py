"""gview.py MACHINE K LOG10STEPS [SEP=00]: real blank-tape run with ms2.exe; print the last snapshot (>= 10^LOG10STEPS)
as raw init-format tape (line 1) and as groups split at SEP (line 2)."""
import subprocess, sys
m, K, L = sys.argv[1:4]; SEP = sys.argv[4] if len(sys.argv) > 4 else '00'
o = subprocess.run([r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\hand\real\ms2.exe', m, K, '400000000000', 'g0', 'x', L, '1'], capture_output=True, text=True, creationflags=0x40, timeout=300).stdout.strip().splitlines()
l = o[-1].replace('SLIM ', ''); a, b = l.split('|', 1); f = a.split()
print(f[2], f[3], f[4], '|', b.strip()[:3000] if '--raw' in sys.argv else '')
gs = [[]]
for x in b.split():
    s, n = (x.split('^') + ['1'])[:2]
    if s == SEP:
        for _ in range(int(n)): gs.append([])
    else: gs[-1].append(s if n == '1' else s + '^' + n)
gs = ['.'.join(g) or '-' for g in gs]; out = []; i = 0
while i < len(gs):
    j = i
    while j + 1 < len(gs) and gs[j + 1] == gs[i]: j += 1
    out.append(gs[i] if j == i else f'[{gs[i]}]x{j-i+1}'); i = j + 1
print('   ', ' | '.join(out)[:400])
