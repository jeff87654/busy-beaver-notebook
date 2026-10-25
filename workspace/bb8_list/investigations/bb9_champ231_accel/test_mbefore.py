import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tm = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH"
tr = parse_tm(tm)

for m_before in range(1, 10):
    u = 50
    s_right = "100" + "1"*u + "00"*m_before + "10000" + "1100"*6 + "1"
    tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
    h, q = 0, 4
    c1_seen = 0
    for step in range(1, 100000):
        b = tape.get(h, 0)
        if q == 2 and b == 1 and c1_seen == 0:
            c1_seen = 1
            mn, mx = min(min(tape), h), max(max(tape), h)
            l_str = "".join(str(tape.get(i, 0)) for i in range(mn, h))
            r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, min(mx+1, h+30)))
            print(f"m_before={m_before} (k={m_before+3}): hits C1 at step {step}: {l_str}[C1]{r_str}...")
        act = tr[2*q + b]
        if act == "---":
            print(f"  -> HALT({chr(65+q)}{b}) at step {step}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        if c1_seen and q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1:
            mx = max(tape)
            r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
            if r_str.startswith("100") or r_str.startswith("1100"):
                parts = r_str[:-3].split("00")
                print(f"  -> step {step}: CLEAN_LEFT [E0] runs={[len(p) for p in parts[:8]]}")
                break
