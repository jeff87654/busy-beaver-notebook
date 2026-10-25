import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

trans = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")

def trace_exh(k, B):
    cfg = "E[0]" + ("1" * B) + ("00" * k) + "001"
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    print(f"=== Trace exhaustion k={k}, B={B}: {cfg} ===")
    for step in range(1, 5000):
        v = tape.get(head, 0)
        t = trans[(state, v)]
        if t is None:
            print(f"  step {step-1:4d} (HALT): {format_tape(tape, head, state)}")
            break
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
        if step <= 120 or state == 2 or head <= min(tape.keys()) or head >= max(tape.keys()):
            if step <= 80 or step >= 200:
                print(f"  step {step:4d}: {format_tape(tape, head, state)}")

trace_exh(3, 11)
