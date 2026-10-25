import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

for name, tm, is_232 in [
    ("champ_231", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", False),
    ("champ_232", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", True),
]:
    print(f"=== {name} ===")
    tr = parse_tm(tm)
    for m in [0, 1, 2]:
        for u in [1, 3, 5]:
            s_right = "100" + "1"*u + "00"*(m+1) + "11"
            tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
            h, q = 0, 4
            exp_step = 3*u*u + 33*u + 56 + 12*u*m + 22*m - 4*m*m + (2*(m+1) if is_232 else 0)
            exp_h = -(2*u + 4)
            exp_str = "100" + "1100"*m + "1"*(3*u + 6 - 2*m)
            for step in range(1, exp_step + 1):
                b = tape.get(h, 0)
                act = tr[2*q + b]
                if int(act[0]): tape[h] = 1
                else: tape.pop(h, None)
                h += 1 if act[1] == 'R' else -1
                q = ord(act[2]) - 65
            mx = max(tape)
            out_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
            match = (q == 4 and tape.get(h, 0) == 0 and h == exp_h and min(tape) == h+1 and out_str == exp_str)
            print(f"  m={m}, u={u}: step={exp_step:4d}, h={h:3d} (exp {exp_h:3d}), exact_match={match}")
