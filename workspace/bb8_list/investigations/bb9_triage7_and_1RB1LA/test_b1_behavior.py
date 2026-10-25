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

tm = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RI0RG"
tr = parse_tm9(tm)

# Test what [E0] 1100 (11)^a 00 (11)^d1 00 ... 1 does for small a, d1!
for label, s_init in [
    ("b=1, a=1, d1=1", "1100110011001"),
    ("b=1, a=2, d1=1", "110011110011001"),
    ("b=1, a=1, d1=2", "110011001111001"),
    ("b=1, a=2, d1=0, d2=1", "11001111000011001"),
]:
    print(f"\n=== Test {label}: [E0]{s_init} ===")
    tape = {i: int(c) for i, c in enumerate(s_init) if c == '1'}
    h, s = -1, 4 # [E0] to the left of s_init
    for step in range(1, 50000):
        b = tape.get(h, 0)
        act = tr[2*s + b]
        if act == "---":
            print(f"  step {step:5d}: HALT({chr(65+s)}{b}) {fmt_tape(tape, h, s)}")
            break
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        ones = [i for i, v in tape.items() if v == 1]
        if (s == 4 and tape.get(h, 0) == 0 and h == min(ones) - 1) or s >= 7:
            print(f"  step {step:5d}: {fmt_tape(tape, h, s)}")
