import re
def tokens(word):
    out = []; i = 0; n = len(word)
    while i < n:
        if word[i] == '0':
            j = i
            while j < n and word[j] == '0': j += 1
            out.append('z%d' % (j-i)); i = j; continue
        j = i; m = 0
        while j + 2 < n and word[j+1] == '0' and word[j+2] == '1':
            j += 2; m += 1
        out.append(m); i = j + 1
    return out
def rle(items):
    out = []; prev = None; c = 0
    for x in items + [None]:
        if x == prev: c += 1; continue
        if prev is not None:
            s = ('%d' % prev) if isinstance(prev, int) else prev
            out.append(s if c == 1 else '%s^%d' % (s, c))
        prev = x; c = 1
    return ' '.join(out)
def view(word):
    s = rle(tokens(word))
    s = re.sub(r'((?:3 2 z1 ){2,})', lambda m: '(3 2 z1)^%d ' % (len(m.group(1).split()) // 3), s + ' ')
    return s.strip()
