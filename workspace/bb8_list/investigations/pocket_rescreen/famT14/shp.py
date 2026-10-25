"""shp.py M Q N [ntok]: blank-tape run (mirrored), print events where the first ntok compressed tokens change shape (numbers->#) """
import sys, subprocess, re
from drv import SIM
from cmp import comp
m, q, N = sys.argv[1], sys.argv[2], sys.argv[3]; nt = int(sys.argv[4]) if len(sys.argv) > 4 else 3
p = subprocess.Popen([SIM, m, '1', 'A', '-', '0', N, q, '100000000'], stdout=subprocess.PIPE, text=True)
prev = None; last = None
for l in p.stdout:
    s = l.split(None, 2)
    if s[0] != 'E' or len(s) < 3: print(l.strip()[:200]); continue
    c = comp(s[2]); sh = re.sub(r'\d+', '#', ' '.join(c.split()[:nt]))
    if sh != prev: print(s[1], c[:170])
    prev = sh; last = (s[1], c)
print('last', last[0], last[1][:200])
