"""rbform.py MACHINE TEMPLATE B1 B2 [RSIDE] : for each b, the first tape-end config after the exhaustion whose run count
>= b (the rebuilt list), compressed: repeated 3-token items shown as (..)xN.  Shows the end-form dependence on b."""
import subprocess, sys, os, re
D = os.path.dirname(os.path.abspath(__file__))
m, tp, b1, b2 = sys.argv[1:5]; rs = len(sys.argv) > 5
env = dict(os.environ); 
if rs: env['RSIDE'] = '1'
def comp(toks):
    out = []; i = 0
    while i < len(toks):
        for L in (3, 2):
            seg = toks[i:i+L]; n = 1
            while toks[i+n*L:i+(n+1)*L] == seg: n += 1
            if n >= 3: out.append('(' + ' '.join(seg) + f')x{n}'); i += n * L; break
        else: out.append(toks[i]); i += 1
    return ' '.join(out)
for b in range(int(b1), int(b2) + 1):
    bud = 8 * b * b + 20000
    p = subprocess.run([os.path.join(D, 'xs2.exe'), m, '2', str(bud), tp, 'b', str(b), str(b), '100000'], capture_output=True, text=True, env=env, creationflags=0x40)
    res = None
    for l in p.stdout.splitlines():
        if l.startswith('  '):
            parts = l.split('|', 1); toks = parts[1].split()
            if len(toks) >= b: res = parts[0].split()[1] + ' | ' + comp(toks); break
        elif ' H ' in l: res = l; break
    print(b, res if res else 'none', flush=True)
