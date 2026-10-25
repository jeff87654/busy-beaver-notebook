import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from test_c4_8state_general_k_M import make_exhaustion_tape

tm_str = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0LD"
tr = parse_tm(tm_str)

for k in (2, 3, 4, 5):
    print(f"=== k={k}, M=3 ===")
    tape, head, state = make_exhaustion_tape(k, M=3)
    for step in range(1, 200000):
        v = tape.get(head, 0)
        if state in (2, 7) and v == 1 and step > 100 * k:
            print(f"  step {step:6d}: {chr(ord('A')+state)}[{v}] ones={len(tape)} cfg={format_tape(tape, head, state)[:90]}")
        if state == 4 and v == 0 and head <= min(tape.keys()):
            ft = format_tape(tape, head, state)
            if step < 2000 or "0011100" in ft or "00100" in ft:
                print(f"  step {step:6d}: LEFT E0 ones={len(tape)} cfg={ft[:90]}")
        w, d, ns = tr[(state, v)]
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
