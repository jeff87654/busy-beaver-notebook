from fam import *
import sys
for form in ('PA', 'PB', 'PC'):
    for z in (0, 1, 2):
        for x in (143, 144, 145):
            y = int(sys.argv[1]) if len(sys.argv) > 1 else 100
            m = build(form, z=z, y=y, x=x)
            out, err = run(m, 3 * 10**5)
            if err: print(form, z, y, x, err[0], err[1][:60], err[2][:200]); continue
            st, (f2, v) = out[0]
            print(form, 'z=%d y=%d x=%d' % (z, y, x), '->', f2, v, 'steps', st)
