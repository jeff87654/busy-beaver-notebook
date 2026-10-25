import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

C4_1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
C4_2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

def make_exhaustion_tape(k, M):
    cfg = ('10' * (2*k - 3)) + '11001C[1]1' + ('0011' * M) + '001'
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    return tape, head, state

def trace_full(tm_str, k, M, max_steps=100000):
    tr = parse_tm(tm_str)
    tape, head, state = make_exhaustion_tape(k, M)
    clean_k_hits = []
    c1_visits = []
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 2 and v == 1:
            ft = format_tape(tape, head, state)
            c1_visits.append((step, len(tape), ft[:90]))
        if state == 4 and v == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
            if m:
                b_new = len(m.group(1))
                ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                clean_k_hits.append((step, b_new, ds))
        t = tr.get((state, v))
        if t is None:
            return "HALT", step - 1, len(tape), clean_k_hits, c1_visits, format_tape(tape, head, state)[:90]
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    return "RUN", max_steps, len(tape), clean_k_hits, c1_visits, format_tape(tape, head, state)[:90]

if __name__ == '__main__':
    print("=== 1. Check 8-state 1-halt-slot extensions without break ===")
    for bname, g0 in [("C4_1", "0LD0RB"), ("C4_2", "1LC0RB")]:
        cands = [
            ("0RH", "---", "0LA"),
            ("0RH", "---", "0RB"),
            ("0RH", "---", "1RG"),
            ("1RH", "---", "0LB"),
            ("1RH", "---", "1LA"),
            ("1RH", "---", "1RC"),
        ]
        for c1, h0, h1 in cands:
            tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_{g0}_{h0}{h1}"
            print(f"\n{bname} C1={c1} H0={h0} H1={h1}:")
            for k in (2, 3, 4):
                for M in (1, 2, 3):
                    st, steps, ones, ck, c1v, end_ft = trace_full(tm_str, k, M, max_steps=100000)
                    print(f"  (k={k}, M={M}): {st} step={steps} ones={ones} clean_k={ck[:3]} c1_visits={len(c1v)}")
                    if st == "HALT" and steps > 300:
                        print(f"    HALT cfg: {end_ft}")
                        for cv in c1v[:4]:
                            print(f"    C1 visit: {cv}")
