"""jumpreach.py: literal K->(jump)->next K runs from small-depth K configs: rightmost head cell vs word end, and the
fate of a single right bit at gaps 1, 8, 64, 512, 4096 (first divergence state/sym, outcome tokens)."""
import sys
from rlib import twin, word, L12
cfgs = sys.argv[1].split(';') if len(sys.argv) > 1 else ['2 5 1^79 0^4 43 1 1 1', '2 5 1^79 0^4 43 1^2 1 1', '2 5 1^77 0^2 41 1 1 1', '2^3 5 1^71 0^3 1 43 1^2 1 2']
for c in cfgs:
    w = word(c)
    r = twin(L12, w, 10**7, '-', maxs=4 * 10**9, rcap=600)
    b = r['base']
    print(f'[{c}] -> {b.get("desc", b)}  steps={b.get("steps")} bmax={r["bmax"]} koff={b.get("off")}', flush=True)
    for g in (1, 8, 64, 512, 4096):
        if g > r['bmax']: break
        q = twin(L12, w, g, '1', maxs=4 * 10**9)
        p = q['pat']
        print(f'    bit at gap {g}: first read {q["read"]} ; out {p.get("desc", p.get("raw"))} rem={p.get("rem","")[:40]}', flush=True)
