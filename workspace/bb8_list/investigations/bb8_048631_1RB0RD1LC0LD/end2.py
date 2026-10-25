from fam import *
import sys
forms = sys.argv[1].split(',')
z = int(sys.argv[2]); ys = range(int(sys.argv[3]), int(sys.argv[4])); xs = [int(v) for v in sys.argv[5].split(',')]
for form in forms:
    for y in ys:
        for x in xs:
            m = build(form, z=z, y=y, x=x)
            out, err = run(m, 3 * 10**5)
            if err: print(form, z, y, x, err[0], err[1][:60], err[2][:200], flush=True); continue
            st, (f2, v) = out[0]
            print(form, 'z=%d y=%d x=%d' % (z, y, x), '->', f2, v, 'steps', st, flush=True)
