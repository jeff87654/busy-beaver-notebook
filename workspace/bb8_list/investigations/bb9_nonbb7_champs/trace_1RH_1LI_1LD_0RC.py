import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from backtrack_c4_9state import parse_tm, make_exhaustion_tape, check_valid_odd_k, format_tape

# C4_1 with C1=1RH, H0=0RC, H1=1LI, I0=---, I1=1LD
tm_str = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RC1LI_---1LD"
tr = parse_tm(tm_str)

for k in (2, 3, 4, 5, 6, 7, 8, 20, 21):
    tape, head, state = make_exhaustion_tape(k, M=4)
    print(f"=== k={k:2d}, M=4 ===")
    for step in range(1, 5000):
        v = tape.get(head, 0)
        if state == 4 and v == 0 and head <= min(tape.keys()):
            vok = check_valid_odd_k(tape, head, state)
            ft = format_tape(tape, head, state)
            print(f"  step {step:4d}: LEFT E0 vok={vok is not None} cfg={ft[:90]}")
            if vok is not None:
                print(f"    -> VALID_ODD_K: B={vok[0]}, len(ds)={len(vok[1])}, ds={vok[1]}")
                break
        if state in (2, 7, 8) and step > 100 * k:
            print(f"  step {step:4d}: {chr(ord('A')+state)}[{v}] cfg={format_tape(tape, head, state)[:90]}")
        t = tr.get((state, v))
        if t is None:
            print(f"  HALT at step {step-1} on {chr(ord('A')+state)}{v}! cfg={format_tape(tape, head, state)[:90]}")
            break
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
