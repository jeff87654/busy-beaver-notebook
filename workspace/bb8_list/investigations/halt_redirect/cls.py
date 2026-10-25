"""Classify completions by their first champion phase after the redirected halt (hyb10 K-moment detection).
  python cls.py NODES.tsv BASEKEY OUT.tsv [WORKERS=6] [STEPS=20000000] [BLIST=1,6,11]
NODES.tsv: renum output (machine first column).  Nodes whose redirected slot points into an old state are skipped
(no new state is reachable, so no halt remains).  Per b: K(0^35;0;b) is run with hyb10 (canonical state of the base
template); J = verified champion phase, with its token list.  Verdict GROW if every b gives J and the token count
increases with b, FIXED if J with a constant count, else the kinds."""
import re, subprocess, sys, tempfile, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
HYB = str(Path(__file__).resolve().parent.parent / 'bb10_bb7_descendants' / 'hyb10r.exe')
src, key, dst = sys.argv[1], sys.argv[2], Path(sys.argv[3])
W = int(sys.argv[4]) if len(sys.argv) > 4 else 6
STEPS = sys.argv[5] if len(sys.argv) > 5 else '20000000'
BL = [int(x) for x in (sys.argv[6] if len(sys.argv) > 6 else '1,6,11').split(',')]
q, P, u, s, be, alB, beB, S = gen.tmpl(gen.C35[key][1])
words = {}
for b in BL:
    w = P + (u * be + s) * 36 + u * (alB * b + beB) + S
    fd, p = tempfile.mkstemp(suffix='.txt'); os.write(fd, w.encode()); os.close(fd); words[b] = (p, len(w))
ms = [l.split('\t')[0] for l in Path(src).read_text().splitlines() if l and not l.startswith('#')]
ms = [m for m in ms if m.split('_')[4][2] >= 'I']          # E0 must enter a new state
done = set(l.split('\t')[0] for l in dst.read_text().splitlines()) if dst.exists() else set()
ms = [m for m in dict.fromkeys(ms) if m not in done]
def ntok(body):
    n = 0
    for t in body.split():
        g = re.fullmatch(r'(\d+)\*(\d+)', t)
        n += int(g.group(2)) if g else 1
    return n
def job(m):
    outs = []
    for b in BL:
        p, L = words[b]
        r = subprocess.run([HYB, m, p, str(L), q, STEPS, '-q', q], capture_output=True, text=True, creationflags=LOW)
        last = (r.stdout.strip().splitlines() or ['? 0'])[-1]
        head, _, body = last.partition(' | ')
        f = head.split()
        outs.append((f[0], f[1], body.strip(), ntok(body) if f[0] == 'J' else -1))
    kinds = ''.join(o[0] for o in outs)
    if set(kinds) == {'J'}:
        c = [o[3] for o in outs]
        v = 'GROW' if all(x < y for x, y in zip(c, c[1:])) else 'FIXED' if len(set(c)) == 1 else 'JMIX'
    else:
        v = kinds
    return m, v, outs
with ThreadPoolExecutor(W) as ex, dst.open('a') as f:
    for m, v, outs in ex.map(job, ms):
        f.write(m + '\t' + v + '\t' + '\t'.join(f'{k}:{st}:{body[:160]}' for k, st, body, _ in outs) + '\n'); f.flush()
print('classified', len(ms))
