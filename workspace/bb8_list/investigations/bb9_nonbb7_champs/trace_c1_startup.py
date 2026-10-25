import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape
from check_c1_new_rebuilders import step_tr

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def trace_startup():
    tr = parse_tm(C1_NEW)
    tape, head, state = {}, 0, 0
    for step in range(1, 2200):
        tape, head, state = step_tr(tr, tape, head, state)
        if state == -1:
            print(f"HALT at step {step}: {format_tape(tape, head, 4)}")
            break
        if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
            cstr = format_tape(tape, head, state)
            if not cstr.endswith("001001B[0]"):
                print(f"step {step:4d}: {cstr}")

if __name__ == '__main__':
    trace_startup()
