"""mkstarts.py TAG -> starts_TAG.txt: E-configurations K(;A;B0) (branch flag 1)."""
import idle, sys
from bcfg import *
tag = sys.argv[1]; M, tt, B0, fam = BASES[tag]; t = T(tag)
with open(f'starts_{tag}.txt', 'w') as f:
    for A in list(range(1, 9)) + [15, 16]:
        w = word(tag, [], A, B0); f.write(f"E{A} {w} {len(w)} {t['q']} 1\n")
print(' '.join([M] + targs(tag)), B0)
