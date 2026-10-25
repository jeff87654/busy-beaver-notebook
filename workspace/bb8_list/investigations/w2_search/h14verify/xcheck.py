"""cross-check stage.exe against the plain Python simulator sim.py (first B-form after a start B-form)"""
import sys
from sim import TM, H14, fare, bword, tokens as stoks
import absim
for (k, w, f) in [(20, 30, 40), (23, 31, 43), (5, 9, 13)]:
    word = fare(k) + bword([0] + [1] * w, f)
    r = absim.Runner().run(H14, 'H', len(word), word, 10**9)
    m = TM(H14, word)
    m.step()
    while True:
        if not m.step(): print('halt'); break
        if m.q == 'H':
            wd, rel, a = m.word()
            if rel == len(wd):
                it = stoks(wd)
                if len(it) >= 2 and it[-2] == 0 and isinstance(it[-1], int): break
    wd, rel, a = m.word()
    print(k, w, f, r['kind'], r['steps'], m.steps, r['word'] == wd)
