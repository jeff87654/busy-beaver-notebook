import sys
fn = sys.argv[1]
lines = open(fn).read().split('\n'); res = []; buf = None
for ln in lines:
    if buf is not None:
        buf += '\\n' + ln
        if ln.count('"') % 2 == 1: res.append(buf); buf = None
        continue
    if ('printf("' in ln or 'printf(stderr, "' in ln) and ln.count('"') % 2 == 1:
        buf = ln; continue
    res.append(ln)
open(fn, 'w').write('\n'.join(res))
