import sys
from tmlib import *
from collections import Counter
tm = {'main': MAIN, 'v1': VAR1, 'v2': VAR2}[sys.argv[1]]
sim = Sim(tm, expand(sys.argv[2]))
ctx = Counter(); examples = {}
steps_limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10**6
while sim.steps < steps_limit:
    if sim.state == 7 and sim.tape[sim.pos] == 1:
        t = sim.tape; p = sim.pos
        k = ''.join(map(str, t[p-6:p])) + '[' + str(t[p]) + ']' + ''.join(map(str, t[p+1:p+7]))
        # record next 6 states
        s2 = Sim.__new__(Sim); s2.__dict__.update(sim.__dict__); s2.tape = bytearray(sim.tape)
        seq = []
        for _ in range(8):
            seq.append(ST[s2.state] + str(s2.tape[s2.pos]))
            if not s2.step(): seq.append('HALT'); break
        key = (k, ' '.join(seq))
        ctx[key] += 1
    if not sim.step(): print('halt'); break
    r = None
for (k, seq), n in ctx.most_common(20):
    print(n, k, seq)
