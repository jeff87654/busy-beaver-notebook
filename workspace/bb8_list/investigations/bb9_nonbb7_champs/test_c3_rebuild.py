import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

trans_c3 = parse_tm("1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE")

def trace_c3_rebuild(name, cfg, max_steps=500000):
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    print(f"=== {name}: {cfg} ===")
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        t = trans_c3[(state, v)]
        if t is None:
            print(f"  step {step-1}: HALT on {chr(ord('A')+state)}{v}: {format_tape(tape, head, state)}")
            return
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
        # Check if head is at right edge in state E or B
        if head >= max(tape.keys()) and state in (1, 4):
            ft = format_tape(tape, head, state)
            if ft.endswith("11B[1]") or ft.endswith("0011E[1]"):
                print(f"  step {step:7d}: Right edge: len={len(ft)}, count(101)={ft.count('101')}, tail={ft[-30:]}")
        # Check if "0000" appears right after G[1]
        if state == 6 and tape.get(head, 0) == 1:
            ft = format_tape(tape, head, state)
            if "G[1]0000" in ft:
                c_twos = ft.count("000101")
                print(f"  step {step:7d}: REBUILT K(0, 2^{c_twos}): {ft[:60]} ... {ft[-40:]}")

# Test 1: k_twos = 0: 101001010B[1]10 00 10 00 101
trace_c3_rebuild("k_twos=0", "101001010B[1]10001000101", 300000)

# Test 2: What if there are z zero digits (00)^z before 101?
for z in [1, 2, 3]:
    trace_c3_rebuild(f"z={z} zeros before 101", "1010010101010B[1]10" + ("00" * z) + "101", 300000)
