import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape
from check_c1_new_rebuilders import step_tr
from verify_c1_new_class2_exact import make_tape_from_str

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def trace_11011():
    tr = parse_tm(C1_NEW)
    # Test 11011 (01)^4 1 0101 00111001 B[0] when it reaches 110111 (01)^6 00111001 B[0]:
    cfg = "110111" + ("01" * 6) + "00111001B[0]"
    tape, head, state = make_tape_from_str(cfg)
    print(f"Start: {format_tape(tape, head, state)}")
    for step in range(1, 500):
        tape, head, state = step_tr(tr, tape, head, state)
        if head <= 8 or (state == 1 and tape.get(head, 0) == 0 and head > max(tape.keys())):
            print(f"  step {step:3d}: {format_tape(tape, head, state)}")

if __name__ == '__main__':
    trace_11011()
