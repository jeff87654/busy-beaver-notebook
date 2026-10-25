import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
import re

def parse_c4_list(s):
    # Check if tape matches E[0] 1^a (00 (11)^d)* 00 1
    m = re.match(r'^(1*)E\[0\](1+)((?:00(?:11)*)*)001$', s)
    if not m:
        return None
    left_ones, right_ones, mid = m.groups()
    a = len(left_ones)
    b = len(right_ones)
    if mid == "":
        ds = []
    else:
        parts = mid.split("00")[1:]
        ds = [len(p)//2 for p in parts]
    return (ds, a, b)

def trace_c4(tm_str, k_ones, max_steps=10000000):
    trans = parse_tm(tm_str)
    tape_str = "E[0]11111" + ("0011" * k_ones) + "001"
    tape = {}
    pos = 0
    i = 0
    while i < len(tape_str):
        if tape_str[i].isalpha():
            state = ord(tape_str[i]) - ord('A')
            v = int(tape_str[i+2])
            if v == 1: tape[pos] = 1
            head = pos
            pos += 1
            i += 4
        else:
            if int(tape_str[i]) == 1: tape[pos] = 1
            pos += 1
            i += 1
    print(f"=== Trace C4 (k={k_ones}) ===")
    last_print = 0
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        t = trans.get((state, v))
        if t is None:
            print(f"  step {step-1:8d}: HALT on {chr(ord('A')+state)}{v}: {format_tape(tape, head, state)}")
            return
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        state = ns
        # Check if state == E (4) and v == 0 at left edge
        if state == 4 and tape.get(head, 0) == 0 and ( not tape or head <= min(tape.keys()) ):
            s = format_tape(tape, head, state)
            parsed = parse_c4_list(s)
            if parsed:
                ds, a, b = parsed
                # reverse ds so most significant is first, like kview
                print(f"  step {step:8d}: K({list(reversed(ds))}; a={a}; b={b})")
            else:
                print(f"  step {step:8d}: Left E[0]: {s[:100]}")
        elif step < 6000 and state == 2: # C
            s = format_tape(tape, head, state)
            if "0000" in s or step > 400:
                pass

for k in [0, 1, 2, 3]:
    trace_c4("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", k, 5000000)
