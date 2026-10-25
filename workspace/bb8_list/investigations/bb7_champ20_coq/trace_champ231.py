import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

def dump_k(tm_str, max_steps=10000):
    rows = tm_str.split("_")
    tr = [t for row in rows for t in (row[:3], row[3:])]
    tape = {}
    h = 0; s = 0
    for step in range(1, max_steps + 1):
        b = tape.get(h, 0)
        act = tr[2 * s + b]
        tape[h] = int(act[0])
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
        if s == 4 and all(tape.get(i, 0) == 0 for i in range(min(min(tape), h), h + 1)):
            mx = max(k for k, v in tape.items() if v == 1)
            bits = "".join(str(tape.get(i, 0)) for i in range(h + 1, mx + 1))
            if bits.startswith("100"):
                print(f"step {step:4d}: <E {bits}")

print("=== M1 ===")
dump_k(M1)
print("=== M2 ===")
dump_k(M2)
