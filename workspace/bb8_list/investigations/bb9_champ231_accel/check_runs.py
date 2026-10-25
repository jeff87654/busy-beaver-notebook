import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tm = "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI1RD_1RD---"
tr = parse_tm(tm)

for a in [1, 2, 3]:
    # Start directly at [E0] 100 (11)^a 00 1 00 11 00 11 00 1
    s_right = "100" + "11"*a + "00100110011001"
    tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
    h, q = 0, 4
    for step in range(1, 20000):
        b = tape.get(h, 0)
        act = tr[2*q + b]
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1:
            mx = max(tape)
            r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
            if r_str.startswith("100") and r_str.endswith("001") and step > 20*a*a:
                parts = r_str[3:-3].split("00")
                if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                    print(f"a={a} -> step={step:5d}: 100% CLEAN b=0 K! vals={[len(p)//2 for p in parts]}")
                    break
