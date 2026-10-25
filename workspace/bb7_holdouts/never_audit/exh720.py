"""exh720.py JSONL OUT [N]: for the first N audited rows (by order in JSONL), the symbolic exhaustion [X]+TF in EVERY
class X = r mod 720 (r = 0..719, X >= 1000): HALT / next K-config / other.  Sound per class (symsim)."""
import sys, json, idle_guard, collections
from fam import *
from coding import VCoding, U10Coding, ChampCoding
CODINGS = {'V': VCoding(), 'U10': U10Coding(), 'U10s2': U10Coding(2), 'U110': U10Coding(1, 2), 'C1': ChampCoding()}
src, dst = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
rows = [json.loads(l) for l in open(src)][:min(N, 6)]
done = set()
try: done = set(json.loads(l)['machine'] for l in open(dst))
except Exception: pass
for R in rows:
    if R['machine'] in done or 'template' not in R: continue
    Q, side, TF, Z, cod = R['template']; Z = int(Z); TF = [] if TF == '-' else [int(x) for x in TF.split(',')]
    m = mirror(R['machine']) if side == 'L' else R['machine']; C = CODINGS[cod]
    res = collections.Counter(); halts = []; other = []
    for r in range(720):
        tp = C.encode(['H%d' % r], TF, Z, Q); got = None
        for NS in (3, 12, 48, 200):
            v, st, fin, raw = run_sym(m, Q, tp, stopn=NS, mg=720, hlb=1000, budget=400000, tlimit=60, prove=True)
            for a, t, sd in st:
                try:
                    qq, vv, zz, rb = stop_v(t); d, tf = C.decode(vv, len(TF))
                except Exception: continue
                if zz == Z and len(tf) == len(TF) and all((isinstance(e, int) and e == t2) or (hasattr(e, 'isconst') and e.isconst() and e.const() == t2) for e, t2 in zip(tf, TF)) and d:
                    got = 'K'; break
            if got or v != 'STOP': break
        o = got or v
        res[o] += 1
        if o == 'HALT': halts.append(r)
        elif o != 'K': other.append((r, o))
    out = {'machine': R['machine'], 'counts': dict(res), 'halt_classes': halts, 'other': other[:20]}
    with open(dst, 'a') as f: f.write(json.dumps(out) + '\n')
