# phases.py MACHINE MIRROR Q PRE A MID B STEPS : literal run, events (Q at left blank edge), print only non-bouncer-continuation events
import sys, re, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
from val import expand, EXE
m, mir, Q, pre, A, mid, B, S = sys.argv[1:9]
if mir == '1': m = '_'.join(''.join(t[i:i+3].replace('L','x').replace('R','L').replace('x','R') for i in (0,3)) for t in m.split('_'))
pre = '' if pre == '-' else pre; mid = '' if mid == '-' else mid
out = subprocess.run([EXE, m, S, 'at', Q, 'L', '100000000'], capture_output=True, text=True).stdout.split('\n')
pat = re.compile('^' + pre + '((?:' + A + ')*)' + mid + '((?:' + B + ')*)(.*?)0*$')
prev = None
sh = lambda t: t if len(t) < 50 else t[:20] + '..' + str(len(t)) + '..' + t[-20:]
for ln in out:
    mm = re.match(r'(\d+) \w \|  <\w> (.*)$', ln.strip())
    if not mm: 
        if ln.startswith('HALT'): print(ln)
        continue
    R = expand(mm.group(2)); g = pat.match(R)
    if g:
        x, y, t = len(g.group(1))//len(A), len(g.group(2))//len(B), g.group(3)
        if prev and x > prev[0] and y == prev[1]-1 and t == prev[2]: prev = (x, y, t); continue
        prev = (x, y, t); print(mm.group(1), 'B', x, y, sh(t))
    else:
        prev = None; print(mm.group(1), 'O', sh(R))
