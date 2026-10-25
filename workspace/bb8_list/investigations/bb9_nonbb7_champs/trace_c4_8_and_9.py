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

def trace_machine(base_str, c1_act, h0_act, h1_act, k=3, M=2, max_steps=100000):
    parts = base_str.split('_')
    tm_str = "_".join(parts[:2] + [parts[2][:3] + c1_act] + parts[3:] + [h0_act + h1_act])
    tr = parse_tm(tm_str)
    tape, head, state = make_exhaustion_tape(k, M)
    
    e0_visits = []
    c1_h_visits = []
    in_round2 = False
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 4 and v == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            e0_visits.append((step, len(tape), ft[:100]))
            if step > 10:
                in_round2 = True
        if in_round2 and (state == 7 or (state == 2 and v == 1)):
            ft = format_tape(tape, head, state)
            c1_h_visits.append((step, f"{chr(ord('A')+state)}{v}", len(tape), ft[:100]))
            if len(c1_h_visits) >= 8:
                break
        t = tr.get((state, v))
        if t is None:
            ft = format_tape(tape, head, state)
            return "HALT", step - 1, len(tape), e0_visits, c1_h_visits, ft[:100]
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    ft = format_tape(tape, head, state)
    return "RUN", max_steps, len(tape), e0_visits, c1_h_visits, ft[:100]

if __name__ == '__main__':
    print("=== PART 1: Trace 8-state 1-halt-slot candidates ===")
    halt_cands = [
        ("C4_2", C4_2, "0RH", "---", "1RG"),
        ("C4_2", C4_2, "1RH", "---", "1RG"),
        ("C4_1", C4_1, "0RH", "---", "0LA"),
        ("C4_1", C4_1, "0RH", "---", "0RB"),
    ]
    for bname, bstr, c1, h0, h1 in halt_cands:
        print(f"\n--- {bname} C1={c1} H0={h0} H1={h1} ---")
        for k in (2, 3, 4):
            for M in (1, 2, 3):
                st, steps, ones, e0v, chv, last_ft = trace_machine(bstr, c1, h0, h1, k=k, M=M, max_steps=50000)
                print(f"  k={k}, M={M}: {st} at step {steps} (ones={ones}), E0_count={len(e0v)}")
                if e0v:
                    print(f"    First E0: {e0v[0]}")
                    if len(e0v) > 1:
                        print(f"    Last  E0: {e0v[-1]}")
                print(f"    End cfg:  {last_ft}")

    print("\n=== PART 2: Trace Even-B_new CLEAN_K 8-state gadgets into Round 2 ===")
    even_cands = [
        ("C4_1", C4_1, "1RH", "0LG", "1LH"),
        ("C4_1", C4_1, "0LH", "1LE", "1LH"),
        ("C4_2", C4_2, "1RH", "0LG", "1LH"),
        ("C4_2", C4_2, "0LH", "1LE", "1LH"),
    ]
    for bname, bstr, c1, h0, h1 in even_cands:
        print(f"\n--- {bname} C1={c1} H0={h0} H1={h1} ---")
        for k in (2, 3):
            for M in (2, 3):
                st, steps, ones, e0v, chv, last_ft = trace_machine(bstr, c1, h0, h1, k=k, M=M, max_steps=100000)
                print(f"  k={k}, M={M}: {st} at step {steps} (ones={ones}), E0_count={len(e0v)}")
                if e0v:
                    print(f"    First E0: {e0v[0]}")
                for v in chv[:4]:
                    print(f"    Round2 C1/H visit: {v}")
