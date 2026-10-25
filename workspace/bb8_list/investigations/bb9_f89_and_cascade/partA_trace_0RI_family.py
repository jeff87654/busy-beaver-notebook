import os, re
import partA_verify_towers as p

tms = [
    ("I1=0LC", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0LC"),
    ("I1=0LE", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0LE"),
    ("I1=0RB", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0RB"),
    ("I1=0RC", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0RC"),
    ("I1=0RD", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0RD"),
    ("I1=0RF", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0RF"),
    ("I1=0RH", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0RH"),
    ("I1=1LE", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---1LE"),
    ("I1=1LF", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---1LF"),
    ("I1=1RA", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---1RA"),
    ("I1=1RE", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---1RE"),
    ("I1=1RH", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---1RH"),
    ("FamA2a_0RI0RF_1LI0RH", "1RB0RE_0RC---_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_0RI0RF_1LI0RH"),
]

for name, tm in tms:
    print("\n" + "="*95)
    print(f"{name}: {tm}")
    t = p.parse_tm(tm)
    tape = {3:1, 5:1} if "FamA2a" in name else {}
    h = 0; s = 'D'; mv = 0
    for step in range(1, 20000):
        c = tape.get(h, 0); tr = t.get((s, c))
        if tr is None:
            print(f"  --> HALT at {s}{c} step={step}")
            break
        w, d, n = tr
        if w: tape[h] = 1
        else: tape.pop(h, None)
        h += d; s = n
        if h < mv:
            mv = h; L = p.check_k(tape, h, s, mv)
            if L is not None:
                print(f"  step {step:5d} (literal K): L = {L} (len={len(L)})")
                changed = False
                iters = 0
                while len(L) >= 2 and iters < 50 and p.step_core_exact(L):
                    changed = True
                    iters += 1
                if changed:
                    print(f"  step {step:5d} (after macro): L = {L} (len={len(L)})")
                    tape = p.write_k(L); h = 0; mv = 0; s = 'D'
