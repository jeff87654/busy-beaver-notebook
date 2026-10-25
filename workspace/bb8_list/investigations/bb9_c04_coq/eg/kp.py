import sys
sys.path.insert(0, '../tools')
from rawparse import kt_of_line
def rl(toks):
    o = []; i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]: j += 1
        o.append('%d*%d' % (toks[i], j - i) if j - i > 1 else str(toks[i])); i = j
    return ' '.join(o)
for line in sys.stdin:
    if line.startswith('K '):
        r = kt_of_line(line)
        if r and r[2] is not None:
            far, toks, m, rr, t = r
            print(line.split()[1], 'far=%r' % far[-30:], rl(toks), '; m=%d r=%d t=%d' % (m, rr, t))
        else: print(line.split()[1], 'RAW', line.split(' ',2)[2][:250].strip())
    else: print(line[:300].strip())
