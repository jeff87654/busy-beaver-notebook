import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm9(tm_str):
    rows = tm_str.split("_")
    return [t for row in rows for t in (row[:3], row[3:])]

def fmt_tape(tape, h, s):
    ones = [i for i, v in tape.items() if v == 1]
    mn = min(ones + [h])
    mx = max(ones + [h])
    left = "".join(str(tape.get(i, 0)) for i in range(mn, h))
    right = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
    return f"{left}[{chr(65+s)}{tape.get(h,0)}]{right}"

# Trace KKHKHK_144 on k=1, 2, 3, 4, 5 with N=4
tm = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"
tr = parse_tm9(tm)

for k in [1, 2, 3, 5]:
    N = 4
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h0 = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    h, s = h0, 2
    print(f"\n=== KKHKHK_144 k={k} (N={N}) ===")
    for step in range(1, 100000):
        b = tape.get(h, 0)
        act = tr[2*s + b]
        if act == "---":
            print(f"  step {step:6d}: HALT({chr(65+s)}{b}) {fmt_tape(tape, h, s)}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        if s >= 7 or (s == 4 and tape.get(h, 0) == 0 and step < 400) or (s == 4 and tape.get(h, 0) == 0 and step > 67000):
            print(f"  step {step:6d}: {fmt_tape(tape, h, s)}")
        if step == 178 and k == 2:
            break
