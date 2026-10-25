from partB_xh0914_analysis import parse_tm, format_tape_window

BASE_231 = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_"

def make_h0_tape(k, U=15, N=5):
    bits = []
    if k == 2:
        bits.extend([1, 0, 0, 1, 1])
    else:
        for _ in range(2*k - 5):
            bits.extend([1, 0])
        bits.extend([1, 1, 0, 0, 1, 1])
    h = len(bits)
    bits.extend([0]*5 + [1]*U + [0]*4)
    for _ in range(N - 1):
        bits.extend([1, 1, 0, 0])
    bits.append(1)
    tape = {i: b for i, b in enumerate(bits) if b != 0}
    return tape, h, 7 # H0

for label, suffix in [
    ("8st H0=0RA", "0RA1RD"),
    ("9st H0=0LI I=---0RF", "0LI1RD_---0RF"),
    ("9st H0=0RI I=1LD---", "0RI1RD_1LD---"),
]:
    print(f"\n=== {label} ===")
    T = parse_tm(BASE_231 + suffix)
    for k in (2, 3, 4):
        tape, pos, q = make_h0_tape(k, U=15, N=5)
        for s in range(1, 300):
            b = tape.get(pos, 0)
            tr = T.get((q, b))
            if tr is None:
                print(f"  k={k}: HALT at {chr(ord('A')+q)}{b} step {s}: {format_tape_window(tape, pos, q)}")
                break
            w, d, nq = tr
            if w == 0: tape.pop(pos, None)
            else: tape[pos] = 1
            pos += d
            q = nq
            lo = min(tape.keys()) if tape else pos
            if q == 4 and tape.get(pos, 0) == 0 and pos < lo:
                print(f"  k={k}: E0 left at step {s}: {format_tape_window(tape, pos, q)}")
                break
