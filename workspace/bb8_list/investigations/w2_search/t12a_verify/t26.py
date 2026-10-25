import lsimpy, sys
M = sys.argv[1]
w = open('w/s329_26.txt').read().strip()
far, t = lsimpy.parse_k(w[:-1])
print(t)
for r in list(range(1, 40)) + [2539, 5059, 7579]:
    ww = far + lsimpy.word_of(t[:-1] + [r]) + '1010'
    x = lsimpy.run(M, ww, kmode=0, maxs=10**8)
    print(r, x['line'][:40])
