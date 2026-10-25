"""view.py MACHINE K MODE MAXMACRO 'TAPE' [--n=40] [--w=200]: ms.exe from TAPE (init format), print compressed tape
(repeated 2/3-token patterns as (..)xN) whenever the count-free skeleton changes."""
import subprocess, sys, re
a = [x for x in sys.argv[1:] if not x.startswith('--')]; o = dict(x[2:].split('=') for x in sys.argv[1:] if x.startswith('--'))
m, K, mode, mm, tp = a[:5]; N = int(o.get('n', '40')); W = int(o.get('w', '200'))
p = subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe', m, K, mm, mode, 'i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, creationflags=0x40)
p.stdin.write(tp + '\n'); p.stdin.close()
def comp(ts):
    for L in (3, 2):
        out = []; i = 0
        while i < len(ts):
            if i + 2 * L <= len(ts) and ts[i:i + L] == ts[i + L:i + 2 * L]:
                j = i
                while j + 2 * L <= len(ts) and ts[j:j + L] == ts[j + L:j + 2 * L]: j += L
                out.append('(' + ' '.join(ts[i:i + L]) + f')x{(j - i) // L + 1}'); i = j + L
            else: out.append(ts[i]); i += 1
        ts = out
    return ' '.join(ts).replace('^1 ', ' ').replace('^1)', ')')
prev = None; c = 0
for l in p.stdout:
    if not l.startswith('T'): print(l.strip()); continue
    x, s = l.split('|', 1); c2 = comp(s.split()); sk = re.sub(r'\^\d+', '', re.sub(r'x\d+', 'x', c2))
    if sk != prev:
        f = x.split(); print(f[1], f[2], f[3], '|', c2[-W:]); prev = sk; c += 1
        if c >= N: break
p.kill()
