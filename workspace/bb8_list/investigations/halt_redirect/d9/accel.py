"""accel.py: affine-period accelerator for token configurations (post-jump K-moment inputs).
compress(tokens) -> list of (motif tuple, count), greedy longest coverage, motif length 1..MAXL.
Accelerator.push(stage, tokens, far) records the config; returns (k, p, new_tokens) when the last three snapshots at
spacing p have the same motif structure, equal far bits, equal last two tokens (a, r), and constant count deltas with
at least one negative delta; k periods are skipped so that every decreasing count stays >= margin."""
MAXL = 6

def compress(t):
    out = []; i = 0; n = len(t)
    while i < n:
        best = (1, 1)   # (L, c)
        for L in range(1, MAXL + 1):
            if i + 2 * L > n: break
            m = t[i:i + L]
            c = 1
            while i + (c + 1) * L <= n and t[i + c * L:i + (c + 1) * L] == m: c += 1
            if c >= 2 and L * c > best[0] * best[1]: best = (L, c)
        L, c = best
        if out and out[-1][0] == tuple(t[i:i + L]):
            out[-1][1] += c
        else:
            out.append([tuple(t[i:i + L]), c])
        i += L * c
    return [(m, c) for m, c in out]

def expand(cm):
    v = []
    for m, c in cm: v += list(m) * c
    return v

class Accelerator:
    def __init__(self, maxp=40, minbig=40, margin_mult=4, margin_min=12):
        self.h = []; self.maxp = maxp; self.minbig = minbig; self.mm = margin_mult; self.mmin = margin_min
    def push(self, stage, toks, far):
        body, ar = toks[:-2], tuple(toks[-2:])
        cm = compress(body)
        self.h.append((stage, tuple(m for m, _ in cm), tuple(c for _, c in cm), ar, far))
        if len(self.h) > 4 * self.maxp + 2: self.h.pop(0)
        if max((c for _, c in cm), default=0) < self.minbig: return None
        cur = self.h[-1]
        for p in range(1, self.maxp + 1):
            if len(self.h) < 3 * p + 1: break
            b, a, z = self.h[-1 - p], self.h[-1 - 2 * p], self.h[-1 - 3 * p]
            if not (cur[1] == b[1] == a[1] == z[1] and cur[3] == b[3] == a[3] == z[3] and cur[4] == b[4] == a[4] == z[4]): continue
            d1 = [x - y for x, y in zip(cur[2], b[2])]; d0 = [x - y for x, y in zip(b[2], a[2])]
            dz = [x - y for x, y in zip(a[2], z[2])]
            if d1 != d0 or d0 != dz or all(d == 0 for d in d1): continue
            if not any(d < 0 for d in d1): continue
            k = min((c - max(self.mmin, self.mm * -d)) // -d for c, d in zip(cur[2], d1) if d < 0)
            if k < 2: return None
            newc = [c + k * d for c, d in zip(cur[2], d1)]
            new = expand(list(zip(cur[1], newc))) + list(cur[3])
            self.h = []
            return k, p, new, d1
        return None
