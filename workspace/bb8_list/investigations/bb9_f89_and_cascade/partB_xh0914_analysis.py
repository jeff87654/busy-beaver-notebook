import os, sys

# Let's inspect the exact tape configuration when xh_0914 and xh_0980 hit H0
# after the 2nd tower collapses, for k = 2, 3, 4, 5, 6.

XH_0914 = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RD"
XH_0980 = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_---1RD"

def parse_tm(code):
    parts = code.strip().split("_")
    T = {}
    for q, p in enumerate(parts):
        for b in (0, 1):
            s = p[3*b:3*b+3]
            if s == "---":
                T[(q, b)] = None
            else:
                T[(q, b)] = (int(s[0]), 1 if s[1] == 'R' else -1, ord(s[2]) - ord('A'))
    return T

def make_e1_tape(k, N_dormant=10):
    # Let's start from the exact pre-exhaustion Kc configuration:
    # b = k - 1 (ones = 2k - 1), a = 0, ds = [0^k], followed by (1100)^N_dormant 1
    #Wait: when a k-digit tower collapses to [0^k], the accumulator b is HUGE (A1),
    # and the final borrow is when ds = [0^k] has m = k > b? No!
    # Wait: how does Exhaustion E happen in champ_231?
    # During Rule D / Borrow, all digits ds collapse until ds = [0^k] and a = 0!
    # Then we have: [E0] 0 1^(2*A1 + 1) 00 (00)^(k+1) 1 (end of tower)!
    # When E0 expands 1^(2*A1 + 1), it turns 1^(2*A1+1) into (1100)^(3*A1+2) 00 (00)^(k+1) 1!
    # Then at the right end of (1100)^(3*A1+2), the last 1100 has b = k - 1 ones?
    # Let's just run from [E0] 0 1^(2*b + 1) 00 (00)^(k+1) 1 with b = 8 (say) to see!
    b = 8
    bits = [0] + [1]*(2*b + 1) + [0, 0] + [0, 0]*(k + 1) + [1]
    tape = {i: bit for i, bit in enumerate(bits) if bit != 0}
    return tape, 0, 4 # state E = 4


def format_tape_window(tape, pos, q, radius=40):
    lo = min(tape.keys()) if tape else pos
    hi = max(tape.keys()) if tape else pos
    lo = min(lo, pos)
    hi = max(hi, pos)
    out = []
    for i in range(lo, hi + 1):
        b = tape.get(i, 0)
        if i == pos:
            out.append(f"[{chr(ord('A')+q)}{b}]")
        else:
            out.append(str(b))
    return "".join(out)

# Notice we can also accelerate E0-configured Kc towers!
# Let's check when state E (q=4) reads 0 at the left end of the tape:
# [E0] 0 1^(2b+1) 00 (11)^a 00 (11)^d1 00 ... (11)^dk 00 1 00 ...
def try_kc_macro(tape, pos, q):
    if q != 4 or tape.get(pos, 0) != 0:
        return None
    lo = min(tape.keys()) if tape else pos
    hi = max(tape.keys()) if tape else pos
    if pos >= lo:
        return None
    if tape.get(pos + 1, 0) != 1:
        return None
    i = pos + 1
    ones = 0
    while i <= hi and tape.get(i, 0) == 1:
        ones += 1
        i += 1
    if ones % 2 != 1:
        return None
    b = (ones - 1) // 2
    if tape.get(i, 0) != 0 or tape.get(i + 1, 0) != 0:
        return None
    i += 2
    fld = []
    kc_end = -1
    while True:
        o = 0
        while i <= hi and tape.get(i, 0) == 1:
            o += 1
            i += 1
        if o == 1 and tape.get(i, 0) == 0 and tape.get(i + 1, 0) == 0:
            kc_end = i - 1
            break
        if o % 2 != 0 or tape.get(i, 0) != 0 or tape.get(i + 1, 0) != 0:
            return None
        fld.append(o // 2)
        i += 2
    if not fld:
        return None
    a = fld[0]
    ds = fld[1:]
    mz = 0
    while mz < len(ds) and ds[mz] == 0:
        mz += 1
    if a > 0:
        nb = b + 3 * a
        fld[0] = 0
    elif mz < len(ds) and mz <= b:
        # Borrow B_mz
        nb = b - mz + 2
        fld[0] = 0
        for j in range(mz):
            ds[j] = 1
        ds[mz] -= 1
        fld = [0] + ds
    else:
        return None
    # Rebuild tape from new_pos to kc_end
    new_bits = [0] + [1]*(2*nb + 1) + [0, 0]
    for v in fld:
        new_bits.extend([1]*(2*v) + [0, 0])
    new_bits.append(1)
    new_pos = kc_end - len(new_bits) + 1
    for idx in range(min(pos, new_pos), kc_end + 1):
        tape.pop(idx, None)
    for offset, bit in enumerate(new_bits):
        if bit:
            tape[new_pos + offset] = 1
    return new_pos

for name, code in [("xh_0914", XH_0914), ("xh_0980", XH_0980)]:
    print(f"=== 100% LITERAL TRACE OF {name} (k=2, b=8) ===")
    T = parse_tm(code)
    for k in (2,):
        tape, pos, q = make_e1_tape(k, N_dormant=6)
        steps = 0
        c1_visits = 0
        while steps < 1000000:
            b = tape.get(pos, 0)
            if q == 2 and b == 1:
                c1_visits += 1
                print(f"    [step {steps}] C1 visit #{c1_visits}: {format_tape_window(tape, pos, q)}")
            tr = T.get((q, b))
            if tr is None:
                print(f"  k={k}: HALT at {chr(ord('A')+q)}{b} after {steps} literal steps, ones={len(tape)}:")
                print(f"    tape: {format_tape_window(tape, pos, q)}")
                break
            w, d, nq = tr
            if w == 0:
                tape.pop(pos, None)
            else:
                tape[pos] = 1
            pos += d
            q = nq
            steps += 1


