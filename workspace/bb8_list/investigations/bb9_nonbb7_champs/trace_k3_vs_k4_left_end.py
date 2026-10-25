import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from test_c4_8state_general_k_M import make_exhaustion_tape

for name, tm_str in [
    ("C4_1 C1=0RH H0=1LC H1=1LH", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LC1LH"),
    ("C4_1 C1=1RH H0=0RB H1=0LD", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0LD"),
]:
    print(f"=== {name} ===")
    tr = parse_tm(tm_str)
    for k in (3, 4):
        print(f"--- k={k} ---")
        tape, head, state = make_exhaustion_tape(k, M=2)
        for step in range(1, 300):
            v = tape.get(head, 0)
            if state in (2, 4, 7):
                print(f"  step {step:3d}: {format_tape(tape, head, state)}")
            w, d, ns = tr[(state, v)]
            if w == 0: tape.pop(head, None)
            else: tape[head] = 1
            head += d; state = ns
            if state == 4 and tape.get(head, 0) == 0 and head <= min(tape.keys()):
                print(f"  step {step+1:3d} (LEFT E0): {format_tape(tape, head, state)}")
                break
