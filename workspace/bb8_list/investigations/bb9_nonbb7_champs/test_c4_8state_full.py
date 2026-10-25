import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

# There are 4 choices for C1 (0LH, 0RH, 1LH, 1RH).
# At (10)^{2k-3} 11001 C[1] 1 (0011)^M 001, both left and right neighbors of C[1] are 1!
# So the first step into H ALWAYS reads H[1]!
# Thus H0 = --- is the ONLY possible halt slot if it doesn't halt at step 2,
# UNLESS H1 steps onto H[0] (i.e. H1 = w d H) and then H0 jumps to A..G while H1 is not --- (no, if H1=wdH then H1 is not ---).
# Wait: what if H1 = w d H, and H1 steps onto a 0 cell, so H0 = w2 d2 X (X in A..G), wait: then neither H0 nor H1 is ---!
# So in 8 states, if H is reached for the first time on H[1], then H1 CANNOT be --- (otherwise it halts immediately in 1 step!).
# Therefore, in ANY non-trivial 8-state halting extension of C4_1 or C4_2, H0 MUST BE ---, and H1 = w2 d2 X (X in A..G)!
# Wait: what if in C4_2 (where G0 = 1LC!), C[1] is entered from G0 = 1LC moving LEFT?!
# HOLD ON! In C4_2, G0 = 1LC moves LEFT into C!

for base_name, g0_str in [("C4_1", "0LD0RB"), ("C4_2", "1LC0RB")]:
    print(f"=== Testing all 8-state halting extensions of {base_name} ({g0_str}) ===")
    for c1 in ["0LH", "0RH", "1LH", "1RH"]:
        for w2 in (0, 1):
            for d2 in ("L", "R"):
                for ns2 in "ABCDEFG":
                    h1 = f"{w2}{d2}{ns2}"
                    tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_{g0_str}_---{h1}"
                    tr = parse_tm(tm_str)
                    # Test on k=2,3 and M=1,2,3
                    results = []
                    interesting = False
                    for k in (2, 3):
                        for M in (1, 2, 3):
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
                            for step in range(1, 50001):
                                v = tape.get(head, 0)
                                t = tr.get((state, v))
                                if t is None:
                                    results.append((k, M, "HALT", step - 1, len(tape)))
                                    if step - 1 > 500:
                                        interesting = True
                                    halted = True
                                    break
                                w, d, ns = t
                                if w == 0: tape.pop(head, None)
                                else: tape[head] = 1
                                head += d; state = ns
                            if not halted:
                                results.append((k, M, "RUN", 50000, len(tape)))
                    if interesting or any(r[2] == "HALT" and r[3] > 50 for r in results):
                        print(f"  C1={c1} H0=--- H1={h1}: {results}")
