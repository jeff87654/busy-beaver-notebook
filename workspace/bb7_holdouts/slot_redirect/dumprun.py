"""dumprun.py MACHINE K DUMP MAXMACRO EVERY [IDX=VAL ...]: ms.exe from an nlp7v dump with edited counts;
prints snapshots whose shape (counts removed) changed, showing the list size and the RIGHT end of the tape."""
import sys, subprocess, re
m, K, dump, mm, pe = sys.argv[1:6]
head, t = open(dump).read().splitlines()[1].split('|', 1); t = t.split()
cut = None
for e in sys.argv[6:]:
    k, v = e.split('=')
    if k == 'CUT': cut = int(v); continue
    i = int(k); t[i] = t[i].split('^')[0] + '^' + v
if cut is not None:
    s0 = 1; n0 = 0
    while t[s0:s0+3] == ['10^1', '01^1', '00^1']: s0 += 3; n0 += 1
    t = t[:1 + 3 * cut] + t[s0:]
ms = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p = subprocess.Popen([ms, m, K, mm, 'p' + pe, 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
p.stdin.write(head + '| ' + ' '.join(t) + '\n'); p.stdin.close()
prev = None
for l in p.stdout:
    l = l.rstrip()
    if not l.startswith('T '): print(l); continue
    a, b = l.split('|', 1)
    b = re.sub(r'(?:10\^1 01\^1 00\^1 ?)+', lambda mo: f'(L)x{mo.group(0).count("00^1")} ', b).replace('^1 ', ' ')
    key = re.sub(r'\^\d+|x\d+', '', b)
    if key != prev: print(' '.join(a.split()[1:4]), '|', b[-300:]); prev = key
