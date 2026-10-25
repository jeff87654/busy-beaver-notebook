"""R4 = phase 1 (shared with the BB(9) champion) + phase 2 (leftward H/I/J pass, 6 steps per block pair) + phase 3.
For b = 0..120 (even): run both champions from Kd [] 0 b to the first G0; compare tape, head and step count;
then check that the BB(10) pass from there is H1 H1 H0 I1 J1 J0 repeated, ending with a fixed tail."""
from kd import *
bad = 0
shapes = {}
for b in range(0, 121, 2):
    sims = []
    for M in (CH10, CH9):
        s = kstart(M, (), 0, b)
        while not (ST[s.state] == 'G' and s.tape[s.pos] == 0):
            assert s.step()
        lo, hi = s.bounds()
        sims.append((s.steps, s.pos - lo, bytes(s.tape[lo:hi + 1]), s))
    same = sims[0][:3] == sims[1][:3]
    s = sims[0][3]
    seq = []
    while True:
        seq.append(ST[s.state] + str(s.tape[s.pos]))
        s.step()
        if s.state == 3 and parse_at(s):
            break
    body = ''.join(seq)
    loop = 'H1H1H0I1J1J0'
    assert body.startswith('G0')
    rest = body[2:]
    pre = ''
    if rest.startswith('H1H0I1J1J0'):
        pre = 'H1H0I1J1J0'
        rest = rest[len(pre):]
    n = 0
    while rest.startswith(loop):
        rest = rest[len(loop):]
        n += 1
    shapes.setdefault((b % 4, pre, rest), []).append((b, n))
    if not same:
        bad += 1
        print('phase 1 differs at b=%d' % b)
for (r, pre, tail), lst in sorted(shapes.items()):
    print('b = %d mod 4: phase 2 = G0 %s [H1H1H0I1J1J0]^k %s for b = %s with k = %s' %
          (r, pre, tail, [x[0] for x in lst][:6] + ['...'], [x[1] for x in lst][:6] + ['...']))
    print('    k = m = (b - %d)/4 for all: %s' % (r, all(k == (bb - r) // 4 for bb, k in lst)))
print('mismatches:', bad)
