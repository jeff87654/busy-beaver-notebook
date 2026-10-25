import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tr = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")

for k in range(1, 7):
    a = k + 2
    s_right = "100" + "1"*(2*a+1) + "00"*k + "001"
    tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
    h, q = 0, 4
    for step in range(1, 50000):
        b = tape.get(h, 0)
        act = tr[2*q + b]
        if act == "---":
            mn, mx = min(min(tape), h), max(max(tape), h)
            cfg = "".join(f"[{chr(65+q)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
            print(f"k={k}, a={a} (step {step:4d}): {cfg}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
