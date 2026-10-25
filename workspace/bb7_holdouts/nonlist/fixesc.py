import sys
B = chr(92); T = chr(9)
f = sys.argv[1]; key = sys.argv[2]
L = open(f).read().split('\n'); out = []; i = 0
while i < len(L):
    l = L[i]
    if key in l:
        if l.count('"') % 2 == 1: l = l + B + 'n' + L[i + 1]; i += 1
        l = l.replace(T, B + 't')
    out.append(l); i += 1
open(f, 'w').write('\n'.join(out))
