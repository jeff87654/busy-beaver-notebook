"""R0: record template K(0^n;0;b) -> first B-form [1^(n+1) | 6b+4] under M10; and the start-up from blank."""
from fw import *
s = Server(M10, 'Bf', 1)
ok = bad = 0
for n in range(1, 13):
    for b in range(0, 7):
        w, h, q = K(n, b)
        x = s.job(w, h, q, 10 ** 9)[-1]
        p = bparse(x['word'], x['rel']) if x['kind'] == 'BF' else None
        if p == ([1] * (n + 1), 6 * b + 4):
            ok += 1
        else:
            bad += 1; print('R0 mismatch', n, b, x['kind'], p)
print('R0 template: %d ok, %d mismatch' % (ok, bad))
x = s.job('0', 0, 'A', 10 ** 7)[-1]
p = bparse(x['word'], x['rel'])
print('blank start: first B-form at step', x['step'], '[%s | %d]' % (fmt(p[0]), p[1]))
s.close()
