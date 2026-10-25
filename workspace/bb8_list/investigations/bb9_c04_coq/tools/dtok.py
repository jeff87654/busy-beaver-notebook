"""dtok.py: D-token view (far->near) of a word: tokens (10)^m 1 -> m, zero gaps -> zN."""
def dtok(w):
    out = []; i = 0; n = len(w)
    while i < n:
        if w[i] == '0':
            j = i
            while j < n and w[j] == '0': j += 1
            out.append('z%d' % (j - i)); i = j; continue
        j = i; m = 0
        while j + 2 < n and w[j:j+3] == '101': j += 2; m += 1
        out.append(str(m)); i = j + 1
    return out
def rle(t):
    o = []; i = 0
    while i < len(t):
        j = i
        while j < len(t) and t[j] == t[i]: j += 1
        o.append('%s*%d' % (t[i], j - i) if j - i > 1 else t[i]); i = j
    return ' '.join(o)
