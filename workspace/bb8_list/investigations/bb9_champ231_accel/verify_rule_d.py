import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm(s):
    return [t for row in s.split("_") for t in (row[:3], row[3:])]

def run_base(tr, k, N, max_steps=200000):
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    h = len(left_str)
    tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
    q = 2
    for step in range(1, max_steps + 1):
        b = tape.get(h, 0)
        act = tr[2*q + b]
        if act == "---":
            return ("H", step, q, b, h, tape)
        if int(act[0]): tape[h] = 1
        else: tape.pop(h, None)
        h += 1 if act[1] == "R" else -1
        q = ord(act[2]) - 65
        if q == 4 and tape.get(h, 0) == 0:
            ones = [i for i, v in tape.items() if v == 1]
            if ones and h == min(ones) - 1:
                mn, mx = min(ones), max(ones)
                r_str = "".join(str(tape.get(i, 0)) for i in range(mn, mx+1))
                w_r = r_str[::-1]
                if w_r.startswith("100") and w_r.endswith("1") and len(w_r) >= 4:
                    parts = w_r[3:-1].split("00")
                    if len(parts) >= 2 and all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                        if len(parts) - 2 >= N - 3:
                            return ("K", step, q, 0, h, tape)
    return ("T", max_steps, q, tape.get(h, 0), h, tape)

def run_accel(tr, k, N, is_232=False, max_iters=200000):
    OFFSET = 200000
    SZ = 400000
    tape = bytearray(SZ)
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    for i, c in enumerate(full_str):
        if c == '1':
            tape[OFFSET + i] = 1
    lo = OFFSET
    hi = OFFSET + len(full_str) - 1
    h = OFFSET + len(left_str)
    q = 2
    step = 0
    iters = 0
    d_const = 58 if is_232 else 56

    while iters < max_iters:
        iters += 1
        # Check K if at E0
        if q == 4 and tape[h] == 0:
            # Find mn, mx
            while lo <= hi and tape[lo] == 0: lo += 1
            while hi >= lo and tape[hi] == 0: hi -= 1
            if lo <= hi and h == lo - 1 and h + 4 <= hi:
                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0 and tape[hi] == 1 and tape[hi-1] == 0 and tape[hi-2] == 0:
                    pos = h + 4
                    ok = True
                    num_runs = 0
                    while pos <= hi - 1:
                        ones = 0
                        while pos <= hi - 1 and tape[pos] == 1:
                            ones += 1
                            pos += 1
                        if ones % 2 != 0 or pos + 1 > hi - 1 or tape[pos] != 0 or tape[pos+1] != 0:
                            ok = False
                            break
                        pos += 2
                        num_runs += 1
                    if ok and num_runs - 1 >= N - 3:
                        out_tape = {i - OFFSET: 1 for i in range(lo, hi+1) if tape[i] == 1}
                        return ("K", step, q, 0, h - OFFSET, out_tape, iters)

            # Try Macro 1: Rule D ([E0] 100 (11)^a 00 11 -> [E0] 100 (11)^(3a+3) 00)
            if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                p = h + 4
                while tape[p] == 1: p += 1
                ones = p - (h + 4)
                if ones % 2 == 0 and tape[p] == 0 and tape[p+1] == 0 and tape[p+2] == 1 and tape[p+3] == 1:
                    a = ones // 2
                    need_left = 4 * a + 4
                    # Check if [h - need_left .. h - 1] is all 0
                    if h < lo or all(tape[i] == 0 for i in range(h - need_left, h)):
                        h_new = h - need_left
                        tape[h+1] = 0
                        tape[p+2] = 0
                        tape[p+3] = 0
                        tape[h_new+1] = 1
                        tape[h_new+2] = 0
                        tape[h_new+3] = 0
                        # Fill 1^(6a+6) from h_new+4 to h+2a+5
                        for i in range(h_new + 4, h + 2*a + 6):
                            tape[i] = 1
                        h = h_new
                        if h - 2 < lo: lo = h - 2
                        step += 12 * a * a + 66 * a + d_const
                        continue

            # Try Macro 2: Expand E0 (0^(2c) [E0] 1^m 00 1^n -> [E0] 1^(m+3c) 00 1^(n-c))
            if tape[h+1] == 1 and tape[h-1] == 0 and tape[h-2] == 0:
                p = h + 1
                while tape[p] == 1: p += 1
                m = p - (h + 1)
                if tape[p] == 0 and tape[p+1] == 0 and tape[p+2] == 1:
                    p2 = p + 2
                    while tape[p2] == 1: p2 += 1
                    n = p2 - (p + 2)
                    # Count how many 00 pairs are available to the left of h (up to n)
                    c = 0
                    while c < n and tape[h - 2*c - 1] == 0 and tape[h - 2*c - 2] == 0:
                        c += 1
                    if c > 0:
                        h_new = h - 2 * c
                        # New 1s block is at [h_new + 1 .. h_new + m + 3*c] = [h - 2*c + 1 .. h + m + c]
                        for i in range(h_new + 1, h + m + c + 1):
                            tape[i] = 1
                        # Next two cells [h + m + c + 1, h + m + c + 2] are 0, 0
                        tape[h + m + c + 1] = 0
                        tape[h + m + c + 2] = 0
                        h = h_new
                        if h - 2 < lo: lo = h - 2
                        step += c * (2 * m + 10) + 3 * c * (c - 1)
                        continue

        # Try Macro 3: Run-skip on B1 (1RB), E1 (1LE), F1 (1LF)
        b = tape[h]
        if b == 1:
            if q == 1: # B1 = 1RB
                p = h + 1
                while tape[p] == 1: p += 1
                d = p - h
                h = p
                step += d
                if h + 2 > hi: hi = h + 2
                continue
            elif q == 4 or q == 5: # E1 = 1LE, F1 = 1LF
                p = h - 1
                while tape[p] == 1: p -= 1
                d = h - p
                h = p
                step += d
                if h - 2 < lo: lo = h - 2
                continue

        slot = 2 * q + b
        act = tr[slot]
        if act == "---":
            out_tape = {i - OFFSET: 1 for i in range(lo, hi+1) if tape[i] == 1}
            return ("H", step + 1, q, b, h - OFFSET, out_tape, iters)
        tape[h] = 1 if act[0] == '1' else 0
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        step += 1
        if h - 2 < lo: lo = h - 2
        if h + 2 > hi: hi = h + 2

    out_tape = {i - OFFSET: 1 for i in range(lo, hi+1) if tape[i] == 1}
    return ("T", step, q, tape[h], h - OFFSET, out_tape, iters)

tm = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"
tr = parse_tm(tm)
for k in [2, 3, 4, 5]:
    r_base = run_base(tr, k, 6, max_steps=100000)
    r_acc = run_accel(tr, k, 6)
    same_kind = (r_base[0] == r_acc[0])
    same_step = (r_base[1] == r_acc[1])
    same_pos = (r_base[2:5] == r_acc[2:5])
    same_tape = (r_base[5] == r_acc[5])
    print(f"k={k}: kind={r_acc[0]} step={r_acc[1]} (exp {r_base[1]}) iters={r_acc[6]:4d} | exact_match={same_kind and same_step and same_pos and same_tape}")
