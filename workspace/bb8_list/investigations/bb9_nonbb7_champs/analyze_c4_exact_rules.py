import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from test_small_lists import run_from_config

# 1. Verify exact string at step 3715 of C4_1 and step 3775 of C4_2
trans1 = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")
tape = {}; head = 0; state = 0
for s in range(1, 3716):
    v = tape.get(head, 0)
    w, d, ns = trans1[(state, v)]
    if w == 0: tape.pop(head, None)
    else: tape[head] = 1
    head += d; state = ns
s3715 = format_tape(tape, head, state)
expected = "E[0]11111" + ("0011" * 20) + "001"
print("Step 3715 matches E[0]11111 + (0011)*20 + 001 ?", s3715 == expected)

# 2. Let's trace a single macro transition from E[0] 1^B 00 (11)^d_0 00 (11)^d_1 ... 001
# Case A: d_0 > 0: E[0] 1^B 00 (11)^{d_0} ...
print("\n--- Testing Case A: d_0 > 0: E[0] 1^B 00 11 001 ---")
for B in [1, 3, 5, 7, 9, 2, 4, 6]:
    cfg = f"E[0]{'1'*B}0011001"
    # run until next Left E[0] with 00 after 1s
    tape = {}; head = 0; state = 4
    for idx, ch in enumerate(cfg[4:]):
        if ch == '1': tape[idx+1] = 1
    for step in range(1, 10000):
        v = tape.get(head, 0)
        t = trans1[(state, v)]
        if t is None:
            print(f"  B={B}: HALT at {step-1}: {format_tape(tape, head, state)}")
            break
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
        if state == 4 and tape.get(head, 0) == 0 and head <= min(tape.keys()):
            ft = format_tape(tape, head, state)
            if ft.startswith("E[0]1") and "001" in ft and not "100111" in ft and not "001001" in ft:
                print(f"  B={B:2d} -> step {step:4d}: {ft}")
                break

# Case B: z >= 1 leading zero digits before a positive digit: E[0] 1^B (00)^z 00 11 001
print("\n--- Testing Case B: z leading zero digits before 11: E[0] 1^B (00)^z 0011 001 ---")
for z in [1, 2, 3, 4]:
    for B in [3, 5, 7, 9, 11, 13, 15, 17, 49]:
        cfg = f"E[0]{'1'*B}{'00'*z}0011001"
        tape = {}; head = 0; state = 4
        for idx, ch in enumerate(cfg[4:]):
            if ch == '1': tape[idx+1] = 1
        for step in range(1, 50000):
            v = tape.get(head, 0)
            t = trans1[(state, v)]
            if t is None:
                print(f"  z={z}, B={B:2d} -> HALT at {step-1}: {format_tape(tape, head, state)}")
                break
            w, d, ns = t
            if w == 0: tape.pop(head, None)
            else: tape[head] = 1
            head += d; state = ns
            if state == 4 and tape.get(head, 0) == 0 and head <= min(tape.keys()):
                ft = format_tape(tape, head, state)
                # check if clean K state: only 00(11)^d blocks
                import re
                if re.match(r'^E\[0\]1+(?:00(?:11)*)*001$', ft):
                    # parse digits
                    m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
                    b_new = len(m.group(1))
                    ds = [len(p)//2 for p in m.group(2).split("00")[1:]]
                    print(f"  z={z}, B={B:2d} -> step {step:5d}: b_new={b_new}, ds(LSB..MSB)={ds}")
                    break
