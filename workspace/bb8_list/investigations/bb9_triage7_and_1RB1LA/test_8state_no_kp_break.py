import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
tr_base = [t for row in M1.split("_") for t in (row[:3], row[3:])]

def parse_K_tape(tape, h, s):
    if s != 4 or tape.get(h, 0) != 0:
        return None
    ones = [i for i, v in tape.items() if v == 1]
    if not ones or h >= min(ones):
        return None
    mn, mx = min(ones), max(ones)
    if h != mn - 1:
        return None
    rev_w = "".join(str(tape.get(i, 0)) for i in range(mn, mx + 1))
    w = rev_w[::-1]
    if not (w.startswith("100") and w.endswith("1")) or len(w) < 4:
        return None
    body = w[3:-1]
    parts = body.split("00")
    if len(parts) < 2:
        return None
    vals = []
    for p in parts:
        if len(p) % 2 != 0 or set(p) - {'1'}:
            return None
        vals.append(len(p) // 2)
    return (vals[:-2], vals[-2], vals[-1])

print("=== Testing all 256 8-state {C1 -> H, H0, H1} completions WITHOUT breaking on KP ===")
for c1_w in "01":
    for c1_d in "LR":
        c1_act = c1_w + c1_d + "H"
        for halt_bit in (0, 1):
            other_bit = 1 - halt_bit
            for h_w in "01":
                for h_d in "LR":
                    for h_st in "ABCDEFGH":
                        h_act = h_w + h_d + h_st
                        tr = list(tr_base) + ["---", "---"]
                        tr[2*2 + 1] = c1_act
                        tr[2*7 + other_bit] = h_act
                        outcomes = {}
                        for k in [1, 2, 3, 4, 5, 6, 7, 8, 20]:
                            N = 25 if k == 20 else 6
                            left_str = "10"*(2*k-1) + "11001"
                            right_str = "100" + "1100"*N + "1"
                            full_str = left_str + "1" + right_str
                            h0 = len(left_str)
                            tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
                            h, s = h0, 2
                            out = "T"
                            for step in range(1, 60000):
                                b = tape.get(h, 0)
                                act = tr[2*s + b]
                                if act == "---":
                                    out = f"H@{step}"
                                    break
                                if int(act[0]): tape[h] = 1
                                else: tape.pop(h, None)
                                h += 1 if act[1] == "R" else -1
                                s = ord(act[2]) - 65
                                parsed = parse_K_tape(tape, h, s)
                                if parsed is not None:
                                    ds_o, a_o, b_o = parsed
                                    if b_o == 0 and len(ds_o) >= N - 3:
                                        out = f"K(len={len(ds_o)},a={a_o})@{step}"
                                        break
                            outcomes[k] = out
                        kinds = {v[0] for v in outcomes.values()}
                        if 'K' in kinds:
                            h0_s = "---" if halt_bit == 0 else h_act
                            h1_s = "---" if halt_bit == 1 else h_act
                            summary = " | ".join(f"k={k}:{outcomes[k]}" for k in [1,2,3,4,5,6,7,8,20])
                            print(f"  C1={c1_act} H={h0_s}{h1_s}: {summary}")
