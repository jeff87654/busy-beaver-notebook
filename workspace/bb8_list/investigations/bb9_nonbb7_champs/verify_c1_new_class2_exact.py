import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape
from check_c1_new_rebuilders import step_tr

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def make_tape_from_str(cfg):
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    return tape, head, state

def test_exact():
    tr = parse_tm(C1_NEW)
    # Class 2: E1=0LH, H0=0LB, H1=---
    tr[(4, 1)] = (0, -1, 7)
    tr[(7, 0)] = (0, -1, 1)
    
    # In Round 2 of Class 2 (for any b >= 3), the tape is:
    # 11 (010101011)^{b-1} (01)^6 0111001 B[0]
    # Let's trace when the leftmost block is at m=2 (11 0101 1) and the next digit is d=0 (011),
    # with accumulator (101)^3 0111001 B[0]:
    cfg = "1101011" + "011" + ("101" * 3) + "0111001B[0]"
    tape, head, state = make_tape_from_str(cfg)
    print(f"Start: {format_tape(tape, head, state)}")
    for step in range(1, 50000):
        v = tape.get(head, 0)
        if (state, v) == (4, 1):
            print(f"HIT E[1] at step {step}: {format_tape(tape, head, state)}")
            break
        tape, head, state = step_tr(tr, tape, head, state)
        if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
            cstr = format_tape(tape, head, state)
            if not cstr.endswith("001001B[0]"):
                print(f"  step {step:5d}: {cstr}")

if __name__ == '__main__':
    test_exact()
