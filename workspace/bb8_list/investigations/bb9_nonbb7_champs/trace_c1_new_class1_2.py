import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape, make_c1_new_halt_tape
from check_c1_new_rebuilders import step_tr

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def test_round2_exhaustion():
    base_tr = parse_tm(C1_NEW)
    STATES = 8
    all_trans = [(w, d, s) for w in (0, 1) for d in (-1, 1) for s in range(STATES)]
    
    # Let's test on smaller initial b (e.g. b=1, 2, 3, 4) for Class 1, Class 2, Class 3, Class 6, etc.
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
        
        for b in (1, 2, 3, 4):
            tape, head, state = make_c1_new_halt_tape(b)
            for step in range(1, 300000):
                v = tape.get(head, 0)
                if (state, v) == (4, 1) and step > 100:
                    print(f"  b={b}: hits E[1] again at step {step}: {format_tape(tape, head, state)[:100]}")
                    break
                tape, head, state = step_tr(tr, tape, head, state)
                if state == -1:
                    print(f"  b={b}: HALTS at step {step}: {format_tape(tape, head, state)[:100]}")
                    break
            else:
                print(f"  b={b}: still running at 300k: {format_tape(tape, head, state)[:100]}")

if __name__ == '__main__':
    test_round2_exhaustion()
