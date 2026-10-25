import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape, make_c1_new_halt_tape
from check_c1_new_rebuilders import step_tr

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def trace_class2():
    tr = parse_tm(C1_NEW)
    tr[(4, 1)] = (0, -1, 7)
    tr[(7, 0)] = (0, -1, 1)
    for b in (1, 2, 3, 4):
        print(f"=== Class 2 (0LH, 0LB, ---) b={b} ===")
        tape, head, state = make_c1_new_halt_tape(b)
        for step in range(1, 100000):
            tape, head, state = step_tr(tr, tape, head, state)
            if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
                cstr = format_tape(tape, head, state)
                if cstr.endswith("1010111001B[0]"):
                    # Count trailing (101) blocks before 0111001B[0]
                    m = re.search(r'((?:101)+)0111001B\[0\]$', cstr)
                    cnt = len(m.group(1)) // 3 if m else 0
                    prefix = cstr[:m.start(1)] if m else cstr
                    print(f"  step {step:6d}: prefix={prefix[:60]} (len={len(prefix)}) (101)^{cnt} 0111001B[0]")

if __name__ == '__main__':
    trace_class2()
