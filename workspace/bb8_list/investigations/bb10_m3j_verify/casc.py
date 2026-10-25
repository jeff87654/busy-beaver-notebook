"""cascade tracer: E0 events from a B-form config; prints the head token's neighbourhood with the long
(D1 D0)^p run compressed.   casc.py LIST:A [MAXEV] [only-left-moving]"""
import sys, re
from fw import *
from btrace import parse_list


def comp(items):
    s = fmt(items)
    s = re.sub(r'((?:D1 D0 ){3,})', lambda m: '(D1 D0)^%d ' % (len(m.group(1).split()) // 2), s + ' ')
    s = re.sub(r'((?:z2 D0 ){3,})', lambda m: '(z2 D0)^%d ' % (len(m.group(1).split()) // 2), s)
    s = re.sub(r'((?:z2 D0\^3 ){3,})', lambda m: '(z2 D0^3)^%d ' % (len(m.group(1).split()) // 2), s)
    s = re.sub(r'((?:z2 D0\^2 ){3,})', lambda m: '(z2 D0^2)^%d ' % (len(m.group(1).split()) // 2), s)
    return s.strip()


if __name__ == '__main__':
    _ts, A = sys.argv[1].rsplit(':', 1)
    w, h, q = bword(parse_list(_ts), int(A))
    mx = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    s = Server(M10, 'Bf,E0', 10 ** 9)
    last = None
    for x in s.job(w, h, q, 10 ** 10):
        if x['kind'] == 'BF':
            p = bparse(x['word'], x['rel']); print('BF', x['step'], '[%s | %d]' % (comp(p[0]), p[1])); break
        if x['kind'] in ('EV', 'HALT'):
            it, idx, off = tokpos(x['word'], x['rel'])
            print(x.get('n', 'HALT'), x['step'], x['q'] + str(x['c']), comp(it[:idx]), '[[', fmt(it[idx:idx + 1]), ']]', comp(it[idx + 1:]))
        else:
            print(x)
        mx -= 1
        if mx <= 0:
            break
    s.close()
