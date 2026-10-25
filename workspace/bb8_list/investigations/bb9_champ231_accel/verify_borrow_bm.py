import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm(s):
    return [t for row in s.split("_") for t in (row[:3], row[3:])]

M231 = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")
M232 = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB")

for name, tr in [("champ_231", M231), ("champ_232", M232)]:
    print(f"=== {name} ===")
    for m in [1, 2, 3]:
        for a in [1, 2, 3, 4]:
            # Initial config at h=0: [E0] 100 (11)^a 00 (00)^m 11
            # Wait: after borrowing from 11, it should become:
            # [E0] 100 11 00 (1100)^(m-1) (11)^(3a+3-m) 00
            s_right = "100" + "11"*a + "00"*(m+1) + "11"
            tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
            h, q = 0, 4 # E0
            min_h, max_h = h, h
            exp_str = "100" + "1100"*m + "11"*(3*a + 3 - m)
            for step in range(1, 20000):
                b = tape.get(h, 0)
                act = tr[2*q + b]
                if int(act[0]): tape[h] = 1
                else: tape.pop(h, None)
                h += 1 if act[1] == 'R' else -1
                q = ord(act[2]) - 65
                if h < min_h: min_h = h
                if h > max_h: max_h = h
                if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1:
                    mx = max(tape)
                    out_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
                    if out_str == exp_str:
                        print(f"  m={m}, a={a}: step={step:4d}, final_h={h:3d}, min_h={min_h:3d}, max_h={max_h:3d} (len_in={len(s_right)})")
                        break
