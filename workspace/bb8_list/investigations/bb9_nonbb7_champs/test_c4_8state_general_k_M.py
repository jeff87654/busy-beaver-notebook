import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

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

def find_first_clean_k_or_halt(tm_str, k, M, max_steps=50000):
    tr = parse_tm(tm_str)
    tape, head, state = make_exhaustion_tape(k, M)
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 4 and v == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
            if m:
                b_new = len(m.group(1))
                ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                return ("CLEAN_K", step, b_new, ds)
        t = tr.get((state, v))
        if t is None:
            return ("HALT", step - 1, len(tape), format_tape(tape, head, state)[:80])
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    return ("TIMEOUT", max_steps, len(tape), format_tape(tape, head, state)[:80])

if __name__ == '__main__':
    cands = [
        ("C4_1", "0LD0RB", "0RH", "---", "0LA"),
        ("C4_1", "0LD0RB", "0RH", "---", "0RB"),
        ("C4_1", "0LD0RB", "0RH", "---", "1RG"),
        ("C4_1", "0LD0RB", "1RH", "---", "0LB"),
        ("C4_1", "0LD0RB", "1RH", "---", "1LA"),
        ("C4_1", "0LD0RB", "1RH", "---", "1RC"),
        ("C4_2", "1LC0RB", "0RH", "---", "1RG"),
    ]
    for bname, g0, c1, h0, h1 in cands:
        tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_{g0}_{h0}{h1}"
        print(f"=== {bname} C1={c1} H0={h0} H1={h1} ===")
        for k in (2, 3, 4, 5, 6, 7, 21):
            row = []
            for M in (1, 2, 3, 4, 5):
                # For k=21, only test M=5,6,10,12 if needed
                res = find_first_clean_k_or_halt(tm_str, k, M, max_steps=30000)
                row.append(f"M={M}:{res[0]}(s={res[1]},b={res[2]},d={res[3] if res[0]=='CLEAN_K' else ''})")
            print(f"  k={k:2d}: " + " | ".join(row))
        # Also test k=21 with M=10, 11, 12, 15, 20
        row21 = []
        for M in (8, 9, 10, 11, 12, 15):
            res = find_first_clean_k_or_halt(tm_str, 21, M, max_steps=50000)
            if res[0] == 'CLEAN_K':
                ds_s = f"len={len(res[3])},head={res[3][:4]}"
            else:
                ds_s = str(res[2])
            row21.append(f"M={M}:{res[0]}(s={res[1]},b={res[2]},{ds_s})")
        print(f"  k=21 (large M): " + " | ".join(row21))
