import c1lib
w = c1lib.kstart(6)
for l in c1lib.job('trace', c1lib.C1, 3_000_000, w, len(w), 'G'): print(l)
