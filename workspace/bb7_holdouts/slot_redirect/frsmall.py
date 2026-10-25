"""frsmall.py MACHINE STATE L a b c x y MAXMACRO EVERY: run ms.exe (K=2) from the constructed fr1-type tape
01^2 (10 01 00)^L 10 00 10^a 01^b 00 10^c 01^x 00 10^y 11 01 [00] in STATE; prints distinct compressed snapshots and the end."""
import sys, subprocess, re
m, q, L, a, b, c, x, y, mm, pe = sys.argv[1:11]
toks = ['01^2'] + ['10^1', '01^1', '00^1'] * int(L) + ['10^1', '00^1', f'10^{a}', f'01^{b}', '00^1', f'10^{c}', f'01^{x}', '00^1', f'10^{y}', '11^1', '01^1', '[00]']
inp = f'{q} 0 | ' + ' '.join(toks) + '\n'
ms = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p = subprocess.Popen([ms, m, '2', mm, 'p' + pe, 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
p.stdin.write(inp); p.stdin.close()
def comp(s):
    s = re.sub(r'((?:10\^1 01\^1 00\^1 ?)+)', lambda mo: f'(L)x{mo.group(1).count("00^1")} ', s)
    return s.replace('^1 ', ' ')
for l in p.stdout:
    l = l.rstrip()
    if l.startswith('T '):
        a_, b_ = l.split('|', 1); print(' '.join(a_.split()[1:4]), '|', comp(b_)[:260])
    else: print(l)
