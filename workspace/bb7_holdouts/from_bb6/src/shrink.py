"""shrink.py SNAPFILE MOD VARIANTS: for each snapshot W line, make shrunken tapes: every maximal run of a period-1..3 unit
with >= 8 reps is cut to r' reps, r' = (r mod MOD) + MOD*j (j=1..VARIANTS); the head's block is kept intact. Prints W lines."""
import sys, re, random
def blocks(s):
    i, out = 0, []
    while i < len(s):
        best = (1, 1)
        for p in (1, 2, 3):
            j = i + p
            while j < len(s) and s[j] == s[j - p]: j += 1
            reps = (j - i) // p
            if reps >= 8 and reps * p > best[0] * best[1]: best = (p, reps)
        out.append((i, s[i:i + best[0]], best[1])); i += best[0] * best[1]
    return out
mod, var = int(sys.argv[2]), int(sys.argv[3]); random.seed(1)
for l in open(sys.argv[1]):
    _, name, tape, pos, q = l.split(); pos = int(pos)
    bl = blocks(tape)
    for j in range(1, var + 1):
        s, np = [], None
        for (i, u, r) in bl:
            ln = len(u) * r
            if r >= 8 and not (i <= pos < i + ln):
                r2 = r % mod + mod * ((j - 1) % 3) + (random.randrange(mod) if j > 3 else 0); s.append(u * r2)
            else:
                if i <= pos < i + ln: np = sum(len(x) for x in s) + (pos - i)
                s.append(u * r)
        print(f"W {name}_s{j} {'00' + ''.join(s) + '00'} {np + 2} {q}")
