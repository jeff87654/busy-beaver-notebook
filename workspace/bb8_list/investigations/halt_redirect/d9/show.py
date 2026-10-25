import sys, re
def comp(s):
    return re.sub(r'(?:10){4,}', lambda m: f'(10)^{len(m.group())//2}', s)
for line in sys.stdin:
    f = line.rstrip('\n').split('\t')
    if f[2] != 'H' or len(f) < 9: print(line[:200]); continue
    w, h = f[7], int(f[8])
    print(f[1], 'steps', f[3], 'ones', f[4], f[5]+f[6], 'len', len(w), 'head', h)
    print('   ', comp(w[:h]), '[' + w[h] + ']', comp(w[h+1:]))
