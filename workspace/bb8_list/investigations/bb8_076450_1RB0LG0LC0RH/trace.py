"""Print every step (tape + head) from a start word, for mechanism inspection."""
import sys
from check_rules import T, Xw, Yw, classify
def trace(word, maxsteps, stop_family=True):
    pad = 20
    tape = [0] * pad + [int(c) for c in word] + [0] * (pad + 40)
    pos = pad - 1; st = 0
    for s in range(maxsteps + 1):
        print('%4d %s' % (s, ''.join(('[%s%d]' % ('ABCDEFGH'[st], v)) if i == pos else str(v) for i, v in enumerate(tape))))
        e = T[st][tape[pos]]
        if e is None: print('HALT'); return
        tape[pos] = e[0]; pos += e[1]; st = e[2]
        if s > 0 and stop_family and st == 0 and tape[pos] == 0 and not any(tape[:pos]):
            w = ''.join(map(str, tape[pos+1:])).rstrip('0')
            if classify(w):
                print('%4d %s  -> %s' % (s + 1, ''.join(('[%s%d]' % ('ABCDEFGH'[st], v)) if i == pos else str(v) for i, v in enumerate(tape)), classify(w))); return
if __name__ == '__main__':
    trace(eval(sys.argv[1]), int(sys.argv[2]))
