import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

candidates = [
    ("C4_2_0RH_1RG", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_---1RG"),
    ("C4_1_0RH_0RB", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RB"),
    ("C4_1_0RH_0LA", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LA"),
]

for name, tm_str in candidates:
    print(f"=== {name}: {tm_str} ===")
    tr = parse_tm(tm_str)
    for k in [2, 3, 4, 5, 6]:
        row = []
        for M in [1, 2, 3, 4, 5, 6]:
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
            halted = False
            for step in range(1, 200001):
                v = tape.get(head, 0)
                t = tr.get((state, v))
                if t is None:
                    row.append(f"M={M}:H@{step-1}(1s={len(tape)})")
                    halted = True
                    break
                w, d, ns = t
                if w == 0: tape.pop(head, None)
                else: tape[head] = 1
                head += d; state = ns
            if not halted:
                row.append(f"M={M}:R(1s={len(tape)})")
        print(f"  k={k}: " + ", ".join(row))
