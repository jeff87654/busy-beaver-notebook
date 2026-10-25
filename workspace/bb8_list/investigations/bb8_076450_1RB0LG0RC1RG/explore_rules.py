import sys
from tmlib import *
tm = {'main': MAIN, 'v1': VAR1, 'v2': VAR2}[sys.argv[1]]
word = sys.argv[2]
nsnap = int(sys.argv[3]) if len(sys.argv) > 3 else 20
sim = Sim(tm, expand(word))
print(0, compress(tokenize(expand(word))))
for i in range(nsnap):
    r = run_until_left(sim, 10**8)
    if r != 'left':
        print(r, sim.steps, sim.show()[:300]); break
    print(sim.steps, compress(tokenize(sim.word())))
