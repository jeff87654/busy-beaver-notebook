"""jumpreach2.py: literal champion-process run from a K config with K-cuts disabled (rcap huge): rightmost head cell
after maxs steps, and the step at which a single bit at gap g is first read (the frontier reaching g)."""
import sys
from rlib import twin, word, L12
c = sys.argv[1] if len(sys.argv) > 1 else '2 5 1^79 0^4 43 1^2 1 1'
w = word(c)
for maxs in (10**5, 10**6, 10**7, 10**8):
    r = twin(L12, w, 10**8, '-', maxs=maxs, rcap=-1)
    print(f'[{c}] maxs={maxs}: bmax={r["bmax"]} ({r["base"].get("raw", r["base"].get("kind"))})', flush=True)
for g in (10, 100, 1000, 10000, 100000):
    q = twin(L12, w, g, '1', maxs=10**8, rcap=-1)
    print(f'    bit at gap {g}: first read at {q["read"]}', flush=True)
