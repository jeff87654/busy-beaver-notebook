from fam import *
res = []
for z in (4, 5, 6, 7, 30):
    for x in (6, 7, 8, 9, 20, 143, 144, 145, 146):
        m = build('PA', z=z, y=4, x=x)
        out, err = run(m, 10**6)
        if err: print(z, x, err[0], err[2][:100]); continue
        st, (f2, v) = out[0]
        print('PA z=%d y=4 x=%d ->' % (z, x), f2, v, 'dy=%d' % (v['y'] - 27 * x))
