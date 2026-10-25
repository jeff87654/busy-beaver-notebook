import re
def tok(s):
    # s: string of 0/1 with optional [X] head marker
    out = []
    i = 0
    while i < len(s):
        if s[i] == '[':
            j = s.index(']', i); out.append(s[i:j+1]); i = j+1; continue
        # try (10)^k with k>=2
        m = re.match(r'(?:10){2,}', s[i:])
        m1 = re.match(r'1+', s[i:]); m0 = re.match(r'0+', s[i:])
        if m and (not m1 or len(m.group(0)) > len(m1.group(0))) :
            k = len(m.group(0))//2
            # don't let the (10) run swallow a head marker - fine since regex stops at '['
            out.append('(10)^%d' % k); i += 2*k; continue
        mm = m1 or m0
        L = len(mm.group(0)); c = s[i]
        out.append(c if L == 1 else '%s^%d' % (c, L)); i += L
    return ' '.join(out)
