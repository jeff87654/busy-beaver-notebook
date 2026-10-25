import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M39 = "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_---0LE_------".split("_")
tr = [t for row in M39 for t in (row[:3], row[3:])]

def test_clear(ds, a=1, b=1):
    bits = []
    for d in ds:
        bits.extend([1]*d + [0])
    bits.extend([1]*a + [0] + [1]*b + [0])
    tape = {i: bit for i, bit in enumerate(bits)}
    h = len(bits)
    s = 2 # C
    min_h = h
    for step in range(1, 500000):
        bit = tape.get(h, 0)
        if h < min_h:
            min_h = h
        act = tr[2*s + bit]
        if act == "---":
            mx = max(tape)
            s_tape = "".join(str(tape.get(i,0)) for i in range(h, mx+1))
            N = s_tape.count("10")
            print(f"ds={ds}: F0 hit at step={step}, h={h} (initial leftmost 1 at 0, min_h={min_h}), N={N}, tape={s_tape[:30]}")
            return
        tape[h] = int(act[0])
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65

for ds in ([1], [2], [3], [1,1], [2,1], [1,1,1]):
    test_clear(ds)
