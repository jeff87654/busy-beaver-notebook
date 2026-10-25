from partB_xh0914_analysis import parse_tm, format_tape_window, XH_0914

T = parse_tm(XH_0914)

def trace_short(bits, max_steps=1000):
    tape = {i: b for i, b in enumerate(bits) if b != 0}
    pos, q = 0, 4 # E0
    for s in range(max_steps):
        lo = min(tape.keys()) if tape else pos
        if q == 4 and tape.get(pos, 0) == 0 and pos < lo:
            print(f"  step {s:4d} (E0 left): {format_tape_window(tape, pos, q)}")
        if q == 2 and tape.get(pos, 0) == 1:
            print(f"  step {s:4d} (C1):      {format_tape_window(tape, pos, q)}")
        b = tape.get(pos, 0)
        tr = T.get((q, b))
        if tr is None:
            print(f"  step {s:4d} (HALT):    {format_tape_window(tape, pos, q)}")
            break
        w, d, nq = tr
        if w == 0: tape.pop(pos, None)
        else: tape[pos] = 1
        pos += d
        q = nq

print("Case 1: [E0] 1^17 (00)^4 1 (nothing after 1)")
trace_short([0] + [1]*17 + [0]*8 + [1])

print("\nCase 2: [E0] 1^17 (00)^3 1 00 1100 1100 1 (dormant suffix after 1 00)")
trace_short([0] + [1]*17 + [0]*6 + [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1])
