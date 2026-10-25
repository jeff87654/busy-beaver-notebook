import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
import lowprio_local, xcheck
p = sys.argv[1]; steps = int(sys.argv[2])
for g in range(10, 22):
    r = xcheck.crosscheck(p, steps, verbose=False, init=(g, 11))
    print(g, r, flush=True)
