from fam import *
for form in ('PA', 'PB', 'PC'):
    for x in (0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 100, 101, 102):
        for y in (40, 41):
            m = build(form, z=10, y=y, x=x)
            out, err = run(m, 10**6)
            if err: print(form, x, y, err); continue
            st, (f2, v) = out[0]
            print(form, 'x=%d y=%d' % (x, y), '->', f2, v, 'dx=%d' % (v['x'] - 27 * x), 'dy=%d' % (v['y'] - y), 'steps', st)
