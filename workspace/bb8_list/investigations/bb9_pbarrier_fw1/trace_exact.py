import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm(m_str, mirror=False):
    tr = {}
    for q, row in enumerate(m_str.split('_')):
        for c in range(2):
            cell = row[3*c:3*c+3]
            if cell[0] != '-':
                w = int(cell[0])
                d = 1 if cell[1] == 'R' else -1
                if mirror:
                    d = -d
                nx = ord(cell[2]) - ord('A')
                tr[(q, c)] = (w, d, nx, f"{chr(65+q)}{c}")
    return tr

def fmt_tape(tape, pos, q, lo_pad=2):
    ks = [k for k, v in tape.items() if v] + [pos]
    lo, hi = min(ks) - lo_pad, max(ks) + lo_pad
    s = []
    for i in range(lo, hi + 1):
        v = str(tape.get(i, 0))
        if i == pos:
            s.append(f"[{chr(65+q)}{v}]")
        else:
            s.append(v)
    return f"(lo={lo}) " + "".join(s)

def run_trace(m_str, mirror, w, head, q_init, max_steps=500, print_every=1, stop_on_q=None):
    tr = parse_tm(m_str, mirror)
    tape = {i: int(ch) for i, ch in enumerate(w) if ch == '1'}
    pos = head
    q = ord(q_init) - ord('A')
    used_slots = []
    used_counts = {}
    print(f"START: {fmt_tape(tape, pos, q)}")
    for st in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        if (q, c) not in tr:
            print(f"step {st}: HALT at {chr(65+q)}{c} {fmt_tape(tape, pos, q)}")
            return used_counts
        w_bit, d, nx, sl = tr[(q, c)]
        used_counts[sl] = used_counts.get(sl, 0) + 1
        tape[pos] = w_bit
        pos += d
        q = nx
        ks = [k for k, v in tape.items() if v]
        at_right_end = (ks and pos > max(ks) and tape.get(pos, 0) == 0)
        if print_every and (st % print_every == 0 or (stop_on_q is not None and q == stop_on_q and at_right_end)):
            print(f"step {st:4d} ({sl}): {fmt_tape(tape, pos, q)}")
        if stop_on_q is not None and q == stop_on_q and at_right_end and st > 1:
            print(f"Reached end-moment in state {chr(65+q)} at step {st}. Slots used: {used_counts}")
    return used_counts

print("=== M4: 1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_1RA1RE (mirror=True, Q=C, P=1, u=01, s=0) ===")
M4 = "1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_1RA1RE"
# Let's trace M4 from blank tape up to step 60 (where first exhaustion [;1;1] happens at step 51!)
print("\n--- M4 from BLANK tape (steps 1..60) ---")
run_trace(M4, True, "", 0, 'A', max_steps=60, print_every=1, stop_on_q=2)

# Now let's trace M4 on:
# 1) R1 (incrementing b): e.g. [1; 2; 1] -> [1; 2; 2]
# Wait: in P=1, u=01, s=0:
# word(ds, a, b) = '1' + ''.join('01'*x + '0' for x in ds + [a]) + '01'*b
def w_m4(ds, a, b):
    return '1' + ''.join('01'*x + '0' for x in list(ds) + [a]) + '01'*b

print("\n--- M4 on [1; 2; 1] (D step: decrement a=2 -> a=1, b=1 -> ... -> [1; 1; 1] -> [1; 0; 4] -> B0 [0; 4; 1]) ---")
w = w_m4([1], 2, 1)
run_trace(M4, True, w, len(w), 'C', max_steps=150, print_every=0, stop_on_q=2)

print("\n--- M4 on [1, 0, 0; 0; 4] (B2 borrow over k=2 zeros with b=4) ---")
w = w_m4([1, 0, 0], 0, 4)
run_trace(M4, True, w, len(w), 'C', max_steps=200, print_every=1, stop_on_q=2)

print("\n--- M4 on [; 2; 1] (Empty list exhaustion E with a=2, b=1 -> [; 0; 7] -> rebuild [1^7; 1; 1]) ---")
w = w_m4([], 2, 1)
run_trace(M4, True, w, len(w), 'C', max_steps=400, print_every=1, stop_on_q=2)
