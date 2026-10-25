import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

# Let's trace KKTKKT_231_R on k=3 like trace_khtkht_k3.py!
tm = "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI1RD_1RD---"
tr = parse_tm(tm)
OFFSET = 300000
SZ = 600000
tape = bytearray(SZ)
k = 3; N = 6
left_str = "10"*(2*k-1) + "11001"
right_str = "100" + "1100"*N + "1"
full_str = left_str + "1" + right_str
for i, c in enumerate(full_str):
    if c == '1': tape[OFFSET + i] = 1
lo = OFFSET; hi = OFFSET + len(full_str) - 1
h = OFFSET + len(left_str); q = 2; step = 0
MIN_SAFE_H = 100

for iters in range(1, 1000):
    if q == 4 and tape[h] == 0:
        while lo <= hi and tape[lo] == 0: lo += 1
        while hi >= lo and tape[hi] == 0: hi -= 1
        if lo <= hi and h == lo - 1:
            runs = []
            p = lo
            while p <= hi:
                v = tape[p]
                p0 = p
                while p <= hi and tape[p] == v: p += 1
                runs.append((v, p - p0))
            if len(runs) <= 25:
                r_desc = " ".join(f"{'1' if v else '0'}^{c}" for v, c in runs)
                print(f"iter={iters:4d} step={step:12d}: [E0] {r_desc}")
                if step > 1000000:
                    break
        if h < lo:
            zeros_left = h - MIN_SAFE_H
        else:
            p_left = h - 1
            while tape[p_left] == 0: p_left -= 1
            zeros_left = h - 1 - p_left
        if zeros_left >= 2 and tape[h+1] == 1:
            p = h + 1
            while tape[p] == 1: p += 1
            m = p - (h + 1)
            if tape[p] == 0 and tape[p+1] == 0 and tape[p+2] == 1:
                p2 = p + 2
                while tape[p2] == 1: p2 += 1
                n = p2 - (p + 2)
                c = min(n, zeros_left // 2)
                if c > 0 and h - 2 * c >= MIN_SAFE_H:
                    h_new = h - 2 * c
                    tape[h_new + 1 : h + m + c + 1] = b'\x01' * (m + 3 * c)
                    tape[h + m + c + 1] = 0
                    tape[h + m + c + 2] = 0
                    h = h_new
                    if h + 1 < lo: lo = h + 1
                    step += c * (2 * m + 10) + 3 * c * (c - 1)
                    continue
    b = tape[h]
    if b == 1:
        if q == 1:
            p = h + 1
            while tape[p] == 1: p += 1
            step += p - h; h = p
            if h + 2 > hi: hi = h + 2
            continue
        elif q == 4 or q == 5:
            p = h - 1
            while tape[p] == 1: p -= 1
            step += h - p; h = p
            if h - 2 < lo: lo = h - 2
            continue
    slot = 2 * q + b
    act = tr[slot]
    if act == "---":
        print(f"HALT at step {step+1}")
        break
    tape[h] = 1 if act[0] == '1' else 0
    h += 1 if act[1] == 'R' else -1
    q = ord(act[2]) - 65
    step += 1
    if h - 2 < lo: lo = h - 2
    if h + 2 > hi: hi = h + 2
