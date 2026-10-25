from fam import *
m = MSim(TM)
a = asim.ASim(m)
n = 0
try:
    while n < 12 and a.nmacro < 10**7:
        a.step()
        r = match(m)
        if r:
            print(a.nmacro, m.steps, r, flush=True); n += 1
except Halt as h:
    print('HALT', h)
