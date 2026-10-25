import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape, make_c1_new_halt_tape
from check_c1_new_rebuilders import step_tr

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def trace_builder():
    base_tr = parse_tm(C1_NEW)
    for name, e1, h0, h1 in [
        ("Class 1 (0LH, 0LA, ---)", (0, -1, 7), (0, -1, 0), None),
        ("Class 2 (0LH, 0LB, ---)", (0, -1, 7), (0, -1, 1), None),
        ("Class 3 (0LH, 0LC, ---)", (0, -1, 7), (0, -1, 2), None),
        ("Class 6 (0LH, 0LD, 0LC)", (0, -1, 7), (0, -1, 3), (0, -1, 2)),
    ]:
        print(f"=== {name} ===")
        tr = dict(base_tr)
        tr[(4, 1)] = e1
        if h0 is not None: tr[(7, 0)] = h0
        if h1 is not None: tr[(7, 1)] = h1
        
        for b in (1, 2, 3, 4, 5, 6):
            tape, head, state = make_c1_new_halt_tape(b)
            print(f"  --- b={b} ---")
            for step in range(1, 5000):
                tape, head, state = step_tr(tr, tape, head, state)
                if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
                    cstr = format_tape(tape, head, state)
                    if not cstr.endswith("001001B[0]"):
                        print(f"    step {step:4d}: {cstr}")
                        if cstr.endswith("1010111001B[0]") or cstr.endswith("110100111001B[0]"):
                            pass
                if (state, tape.get(head, 0)) == (4, 1) and step > 100:
                    print(f"    step {step:4d} HIT E[1]: {format_tape(tape, head, state)}")
                    break

if __name__ == '__main__':
    trace_builder()
