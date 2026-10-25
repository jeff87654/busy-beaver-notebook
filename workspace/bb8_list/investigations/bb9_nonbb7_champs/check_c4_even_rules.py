import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

for name, tm_str in [("C4_1", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"), ("C4_2", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB")]:
    tr = parse_tm(tm_str)
    print(f"=== {name} Even B Refill E[0] 1^B (00)^z 0011 001 ===")
    for z in range(1, 7):
        B = 2 * z + 10
        cfg = "E[0]" + ("1" * B) + ("00" * z) + "0011001"
        tape = {}; head = 0; state = 4
        for idx, ch in enumerate(cfg[4:]):
            if ch == '1': tape[idx+1] = 1
        for step in range(1, 10000):
            v = tape.get(head, 0)
            t = tr[(state, v)]
            if t is None:
                print(f"  z={z}, B={B} -> HALT at {step-1}: {format_tape(tape, head, state)}")
                break
            w, d, ns = t
            if w == 0: tape.pop(head, None)
            else: tape[head] = 1
            head += d; state = ns
            if state == 4 and tape.get(head, 0) == 0 and head <= min(tape.keys()):
                ft = format_tape(tape, head, state)
                m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
                if m:
                    b_new = len(m.group(1))
                    ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                    print(f"  z={z}, B={B} -> step {step:4d}: CLEAN_K B_new={b_new}, ds={ds}")
                    break
    print(f"=== {name} Even B Exhaustion E[0] 1^B (00)^K 001 ===")
    for K in range(1, 7):
        B = 2 * K + 10
        cfg = "E[0]" + ("1" * B) + ("00" * K) + "001"
        tape = {}; head = 0; state = 4
        for idx, ch in enumerate(cfg[4:]):
            if ch == '1': tape[idx+1] = 1
        for step in range(1, 10000):
            v = tape.get(head, 0)
            t = tr[(state, v)]
            if t is None:
                print(f"  K={K}, B={B} -> HALT at {step-1}: {format_tape(tape, head, state)}")
                break
            w, d, ns = t
            if w == 0: tape.pop(head, None)
            else: tape[head] = 1
            head += d; state = ns
            if state == 4 and tape.get(head, 0) == 0 and head <= min(tape.keys()):
                ft = format_tape(tape, head, state)
                m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
                if m:
                    b_new = len(m.group(1))
                    ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                    print(f"  K={K}, B={B} -> step {step:4d}: CLEAN_K B_new={b_new}, ds={ds}")
                    break
