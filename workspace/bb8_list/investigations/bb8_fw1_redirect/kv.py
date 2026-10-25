"""kv.py TAG MACHINE [STEPS] [MAXL]: blank-tape K-trace (real K-moments b=B0 only, list changes) of an 8-state machine in TAG's template."""
import idle, sys
from bcfg import *
tag, M = sys.argv[1], sys.argv[2]; steps = int(sys.argv[3]) if len(sys.argv) > 3 else 10**8; maxl = int(sys.argv[4]) if len(sys.argv) > 4 else 3000
B0 = BASES[tag][2]
ev = kl.blank(M, steps, maxl, T=T(tag)) if False else None
import subprocess
t = T(tag)
p = subprocess.Popen([kl.EXE, M] + kl.args(t) + [str(steps), str(maxl), '1'], creationflags=0x40, stdout=subprocess.PIPE, text=True)
o, _ = p.communicate(); ev = kl.parse(o)
last = None; n = 0
for e in ev:
    if e[0] == 'K' and e[4] != B0: continue
    if e[0] == 'K':
        key = (tuple(e[2]),)
        if key == last: continue
        last = key; ds = e[2]
        s = []; i = 0
        while i < len(ds):
            j = i
            while j < len(ds) and ds[j] == ds[i]: j += 1
            s.append(f"{ds[i]}^{j-i}" if j - i > 2 else ','.join([str(ds[i])] * (j - i))); i = j
        print(e[1], f"[{','.join(s)}; {e[3]}]", f"len={len(ds)}"); n += 1
        if n > 60: break
    elif e[0] == 'H': print('HALT', e[1:])
    elif e[0] == 'END': print('END')
