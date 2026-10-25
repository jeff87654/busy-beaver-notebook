"""Transition usage: blank tape to the first Y(141) (5382 steps) and in each rule on small cases."""
from check_rules import T, Xw, Yw
from collections import Counter
def run_count(word, steps):
    pad = 4000
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1; st = 0; cnt = Counter()
    for _ in range(steps):
        s = tape[pos]; e = T[st][s]
        if e is None: cnt['ABCDEFGH'[st] + str(s) + '(halt)'] += 1; break
        cnt['ABCDEFGH'[st] + str(s)] += 1
        tape[pos] = e[0]; pos += e[1]; st = e[2]
    return cnt
c = run_count('', 5382)
print('blank -> Y(141):', dict(sorted(c.items())))
for name, w, n in [('R1 X(5,3,2)', Xw(5,3,2), 21), ('R2 X(5,0,2)', Xw(5,0,2), 24), ('R3 X(5,0,0)', Xw(5,0,0), 31),
                   ('R4 Y(9)', Yw(9), 44), ('R5 Y(13)', Yw(13), 131), ('R6 Y(8)', Yw(8), 30)]:
    print(name, dict(sorted(run_count(w, n).items())))
