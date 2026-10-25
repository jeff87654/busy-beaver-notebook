import itertools
from lit import parse, MAIN
T = parse(MAIN)
ST = 'ABCDEFGH'
def sim(left, q, right, maxs=200):
    """tape = left + right, head at index len(left) in state q; run until head reaches index len(left)+len(block) ... return trace"""
    tape = list(left) + list(right)
    pos = len(left); st = q; steps = 0
    while steps < maxs:
        if pos < 0 or pos >= len(tape):
            return None
        e = T[st][tape[pos]]
        if e is None: return None
        w, d, s2 = e
        tape[pos] = w; pos += d; st = s2; steps += 1
        yield (pos, st, tuple(tape), steps)
# find: context c (len k) + F> block^2 ; head reaches offset len(c)+len(block) in state F with left part = c' + ... periodic
for blk in [(0,0,1),(0,1,0),(1,0,0)]:
  for q in 'ABCDEFGH':
    for k in range(0, 5):
        for c in itertools.product((0, 1), repeat=k):
            right = blk * 4 + (0,) * 3
            qi = ST.index(q)
            for pos, st, tape, steps in sim(c, qi, right):
                if pos == len(c) + len(blk) and st == qi:
                    # check new context after = old context shifted: tape[len(blk):len(blk)+k] == c
                    newc = tape[len(blk):len(blk) + k]
                    if newc == tuple(c) and tape[len(c)+len(blk):] == right[len(blk):]:
                        print(q, 'block', blk, 'ctx', c, '->', tape[:len(blk)], 'steps', steps)
                    break
                if pos < 0 or pos > len(c) + 2*len(blk): break
