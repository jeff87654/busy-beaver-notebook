"""block compression of a token list: runs of a repeated pattern of length 1..3 -> (pat)^k"""
import re, sys
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v
def blocks(v, maxp=3, minrep=3):
    out = []; i = 0; n = len(v)
    while i < n:
        best = None
        for p in range(1, maxp + 1):
            if i + p > n: break
            k = 1
            while i + (k + 1) * p <= n and v[i + k * p:i + (k + 1) * p] == v[i:i + p]:
                k += 1
            if k >= minrep or (p == 1 and k >= 2):
                if best is None or k * p > best[0] * best[1]:
                    best = (k, p)
        if best:
            k, p = best
            pat = v[i:i + p]
            out.append((tuple(pat), k)); i += k * p
        else:
            out.append(((v[i],), 1)); i += 1
    return out
def fmt(bl):
    s = []
    for pat, k in bl:
        if k == 1: s.append(str(pat[0]))
        elif len(pat) == 1: s.append(f'{pat[0]}^{k}')
        else: s.append('(' + ' '.join(map(str, pat)) + f')^{k}')
    return ' '.join(s)
def compress(s):
    return fmt(blocks(expand(s)))
if __name__ == '__main__':
    for fn in sys.argv[1:]:
        print('=====', fn)
        for line in open(fn):
            line = line.rstrip()
            m = re.match(r'(\d+ [KJ]:.*?(?:->)?)\s*((?:[\d^ ]| )+)\| a=(\d+) r=(\d+)(.*)$', line)
            if m and ('K:' in line or 'J:' in line):
                # split head text from list: for K lines "n K: LIST | a= r=", for J lines "... -> LIST | a= r="
                if 'K:' in line:
                    head, rest = line.split('K: ', 1); head += 'K:'
                else:
                    head, rest = line.split('-> ', 1); head += '->'
                lst, tail = rest.split(' | a=', 1)
                print(head, compress(lst), '| a=' + tail)
            else:
                print(line)
