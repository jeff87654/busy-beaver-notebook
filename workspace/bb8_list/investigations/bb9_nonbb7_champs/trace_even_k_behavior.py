import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from test_c4_8state_general_k_M import make_exhaustion_tape

def trace_gadget_k(base_g0, c1, h0, h1, k, M=4, max_steps=100000):
    tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_{base_g0}_{h0}{h1}"
    tr = parse_tm(tm_str)
    tape, head, state = make_exhaustion_tape(k, M)
    e0_left_hits = []
    c1_hits = []
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 2 and v == 1:
            c1_hits.append((step, len(tape), format_tape(tape, head, state)[:90]))
        if state == 4 and v == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
            if m:
                b_new = len(m.group(1))
                ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                return ("CLEAN_K", step, b_new, ds, e0_left_hits, c1_hits)
            else:
                e0_left_hits.append((step, len(tape), ft[:90]))
        t = tr.get((state, v))
        if t is None:
            return ("HALT", step - 1, len(tape), format_tape(tape, head, state)[:90], e0_left_hits, c1_hits)
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    return ("TIMEOUT", max_steps, len(tape), format_tape(tape, head, state)[:90], e0_left_hits, c1_hits)

if __name__ == '__main__':
    cands = [
        ("C4_2", "1LC0RB", "1LH", "1LG", "1LC"),
        ("C4_1", "0LD0RB", "0RH", "1LC", "1LH"),
        ("C4_2", "1LC0RB", "0RH", "0LD", "1LG"),
        ("C4_1", "0LD0RB", "1RH", "0RB", "0LD"),
        ("C4_1", "0LD0RB", "1LH", "0LF", "1LC"),
        ("C4_2", "1LC0RB", "0RH", "0LA", "1LG"),
    ]
    for bname, g0, c1, h0, h1 in cands:
        print(f"=== {bname} C1={c1} H0={h0} H1={h1} ===")
        for k in (2, 3, 4, 5, 6, 7, 8, 20, 21, 22):
            res = trace_gadget_k(g0, c1, h0, h1, k, M=4, max_steps=50000)
            if res[0] == "CLEAN_K":
                print(f"  k={k:2d}: CLEAN_K step={res[1]} B={res[2]} len(ds)={len(res[3])} ds={res[3]}")
            else:
                print(f"  k={k:2d}: {res[0]} step={res[1]} ones={res[2]} e0_hits={len(res[4])} c1_hits={len(res[5])}")
                for e0 in res[4][:3]:
                    print(f"    E0 hit: {e0}")
                for ch in res[5][:4]:
                    print(f"    C1 hit: {ch}")
