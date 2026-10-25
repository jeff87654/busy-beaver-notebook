import re
def comp(s):
    toks = s.split(); out = []; i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]: j += 1
        t = toks[i]; m = re.match(r'^(\d+)(.*)$', t)
        n = int(m.group(1)); n = str(n) if n <= 9 else 'X'
        t = n + m.group(2); c = j - i
        out.append(t if c == 1 else (t + '^' + ('k' if c > 3 else str(c))))
        i = j
    return ' '.join(out)
