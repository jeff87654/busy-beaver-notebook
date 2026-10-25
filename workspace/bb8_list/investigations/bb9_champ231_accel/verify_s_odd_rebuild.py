import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

for name, tm in [
    ("champ_231", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"),
    ("champ_232", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"),
]:
    print(f"=== {name} ===")
    tr = parse_tm(tm)
    for k in range(1, 7):
        for a in [k + 1, k + 2, k + 3]:
            # S_odd: [E0] 100 1^(2a+1) (00)^k 00 1
            s_right = "100" + "1"*(2*a+1) + "00"*k + "001"
            tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
            h, q = 0, 4
            for step in range(1, 100000):
                b = tape.get(h, 0)
                act = tr[2*q + b]
                if act == "---":
                    print(f"  k={k}, a={a}: HIT C1 at step {step}")
                    break
                if int(act[0]): tape[h] = 1
                else: tape.pop(h, None)
                h += 1 if act[1] == 'R' else -1
                q = ord(act[2]) - 65
                if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1:
                    mx = max(tape)
                    r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
                    if r_str.startswith("100") and r_str.endswith("001"):
                        parts = r_str[3:-3].split("00")
                        if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                            vals = [len(p)//2 for p in parts]
                            a_out = vals[0]
                            ds_out = vals[1:] # in left-to-right tape order: d_1, d_2, ..., d_M
                            print(f"  k={k}, 2a+1={2*a+1:2d} (a={a}): step={step:5d} -> CLEAN b=0 K! a_out={a_out}, len={len(ds_out)} (3a+3-k={3*a+3-k}), d1={ds_out[0]}, rest_all_1={all(x==1 for x in ds_out[1:])}")
                            break
