"""tokrle.py: filter c04raw --dv output: compress repeated token patterns (period <= 8 tokens) as [pat]^k."""
import sys, re
def comp(toks):
    out = []; i = 0; n = len(toks)
    while i < n:
        best = None
        for p in range(1, 9):
            if i + p > n: break
            k = 1
            while toks[i + k * p:i + (k + 1) * p] == toks[i:i + p]: k += 1
            if k >= 2 and k * p >= 3 and (best is None or k * p > best[0] * best[1]): best = (k, p)
        if best:
            k, p = best
            pat = ' '.join(toks[i:i + p]); out.append(('[%s]^%d' % (pat, k)) if p > 1 else '%s^%d' % (pat, k) if '^' not in pat else '[%s]^%d' % (pat, k)); i += k * p
        else:
            out.append(toks[i]); i += 1
    return out
for line in sys.stdin:
    line = line.rstrip('\n')
    m = re.match(r'^(\S+ \d+ )(.*?)( \| .*| \[[A-I]>.*)$', line)
    if not m: print(line); continue
    pre, body, post = m.groups()
    toks = body.split()
    print(pre + ' '.join(comp(toks)) + post[:200])
