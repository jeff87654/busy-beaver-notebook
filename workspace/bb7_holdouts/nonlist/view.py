"""view.py MACHINE K SIDE MAXMACRO [N]: ms.exe trace, print snapshots whose count-free shape changed (first/last N)."""
import re, subprocess, sys
m, K, side, mm = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
N = int(sys.argv[5]) if len(sys.argv) > 5 else 30
ms = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
p = subprocess.run([ms, m, K, mm, side + '1'], capture_output=True, text=True)
prev = None; out = []
for l in p.stdout.splitlines():
    if not l.startswith('T '): 
        if l.strip(): out.append(l)
        continue
    f = l.split('|', 1); t = f[0].split(); body = f[1].strip()
    key = re.sub(r'\^\d+', '^*', body)
    if key != prev: W = int(sys.argv[6]) if len(sys.argv)>6 else 200
    out.append(f"{t[1]:>9} {float(t[2]):.3e} " + (body if len(body) <= W else body[:W//3] + ' ... ' + body[-2*W//3:])); prev = key
print(len(out), 'shape changes')
for o in out[:N]: print(o)
if len(out) > 2 * N: print('...')
for o in out[max(N, len(out) - N):]: print(o)
