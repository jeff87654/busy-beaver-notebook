import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
T_STR = "L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1"
T = kl.tmpl(M1, T_STR)

# Wait: in kl.word(T, ds, a, b), when o == 'L', how does kview.exe lay out the word on the tape?
# In kview.exe, when o == 'L', the word w = P + ds + a + b + S is reversed on the real tape!
# Specifically, let's check step 3897 of the blank-tape run in check_champ231_c1.py:
# At step 3897, it is K(1^19, 0; 8; 0)!
# Let's see the exact real-tape layout of K(ds; a; 0) at step 3897 and step 5459!

tr_base = [t for row in M1.split("_") for t in (row[:3], row[3:])]

tape = {}
h = 0; s = 0
for step in range(1, 5500):
    b = tape.get(h, 0)
    act = tr_base[2*s + b]
    tape[h] = int(act[0])
    h += 1 if act[1] == "R" else -1
    s = ord(act[2]) - 65
    if step in (3715, 3897, 5459):
        mn, mx = min(min(tape), h), max(max(tape), h)
        bits = "".join(f"[{chr(65+s)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
        print(f"Blank step {step}: {bits}")

# In L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1:
# w = "100" + "".join("11"*d + "00" for d in ds + [a]) + "11"*b + "1"
# Since o == 'L', the real tape from LEFT to RIGHT is the REVERSE of w, with [E0] on the LEFT of the reversed word!
# Let's check: reverse of w for K(1^19, 0; 8; 0):
# w = "100" + ("1100")*19 + "00" + ("11")*8 + "00" + "1"
# Reversed w (left to right on real tape):
# [E0] "1" + "00" + ("11")*8 + "00" + ("0011")*19 + "001"
# Let's verify this against Blank step 3897!
w_3897 = kl.word(T, [1]*19 + [0], 8, 0)
rev_3897 = w_3897[::-1]
print(f"Expected rev(w) for K(1^19,0;8;0): [E0]{rev_3897}")

# And when K(0^k; a; 0) starts at [E0] + rev(w(0^k; a; 0)):
# w(0^k; a; 0) = "100" + "00"*k + "11"*a + "00" + "1"
# rev(w(0^k; a; 0)) = "100" + "11"*a + "00"*k + "001"
# Wait: at the end of rev(w), "00" + "001" is "00"*(k+1) + "1"?
# Let's check: w = "100" + "00"*k + "11"*a + "00" + "1"
# Reverse of w:
# "1" + "00" + "11"*a + "00"*k + "001" = "100" + "11"*a + "00"*(k+1) + "1"!
# Wait: that IS "100" + "11"*a + "00" + "00"*k + "1" — the EXACT string in check_champ231_c1.py line 48!

def make_K_tape(ds, a, b=0):
    w = kl.word(T, ds, a, b)
    rev_w = w[::-1]
    tape = {i: int(c) for i, c in enumerate(rev_w) if c == '1'}
    return tape, -1, 4 # h = -1 (just left of rev_w), state = E (4)

def parse_K_tape(tape, h, s):
    # Must be in state E (4), reading 0 at h, with all 1s to the right of h!
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
    # Parse w with P="100", S="1", s="00", u="11"
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
    return (vals[:-2], vals[-2], vals[-1]) # (ds, a, b)

print("\n=== Verify make_K_tape and parse_K_tape on K(0^k; a; 0) hitting C1 ===")
for k in range(1, 7):
    a = k + 1
    tape, h, s = make_K_tape([0]*k, a, 0)
    for st in range(1, 100000):
        b = tape.get(h, 0)
        act = tr_base[2*s + b]
        if act == "---":
            ones = [i for i, v in tape.items() if v == 1]
            mn, mx = min(min(ones), h), max(max(ones), h)
            cfg = "".join(f"[{chr(65+s)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
            expected_cfg = "10"*(2*k-1) + "1100" + "1[C1]100" + "1100"*(3*a+1-k) + "1"
            assert cfg == expected_cfg, f"Mismatch: {cfg} != {expected_cfg}"
            print(f"  k={k}, a={a}: hits C1 at step {st:4d} with EXACT formula: (10)^{2*k-1} 1100 1[C1]100 (1100)^{3*a+1-k} 1")
            break
        tape[h] = int(act[0])
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65

print("\n=== Test all 14 7-state completions of C1 for k = 1..8 (with N = 3a+1-k = 5) ===")
for bit in "01":
    for d in "LR":
        for st_ch in "ABCDEFG":
            cand = bit + d + st_ch
            tr = list(tr_base)
            tr[2*2 + 1] = cand # C1
            row_res = []
            for k in range(1, 9):
                N = 5
                # Start directly from the C1 config: (10)^{2k-1} 1100 1 [C1] 100 (1100)^N 1
                left_str = "10"*(2*k-1) + "11001"
                right_str = "100" + "1100"*N + "1"
                full_str = left_str + "1" + right_str
                h0 = len(left_str)
                tape = {i: int(c) for i, c in enumerate(full_str) if c == '1'}
                h, s = h0, 2 # state C on 1
                outcome = "T"
                for step in range(1, 50000):
                    b = tape.get(h, 0)
                    act = tr[2*s + b]
                    if act == "---":
                        outcome = f"H@{step}"
                        break
                    if int(act[0]): tape[h] = 1
                    else: tape.pop(h, None)
                    h += 1 if act[1] == "R" else -1
                    s = ord(act[2]) - 65
                    parsed = parse_K_tape(tape, h, s)
                    if parsed is not None:
                        ds_out, a_out, b_out = parsed
                        outcome = f"K(len={len(ds_out)},ds={ds_out[:3]}..;a={a_out};b={b_out})"
                        break
                    # Also check if it reached [E0] on 100... with some left garbage!
                    if s == 4 and tape.get(h, 0) == 0 and tape.get(h+1, 0) == 1 and tape.get(h+2, 0) == 0 and tape.get(h+3, 0) == 0:
                        ones = [i for i, v in tape.items() if v == 1]
                        left_ones = [i for i in ones if i < h]
                        if left_ones:
                            l_str = "".join(str(tape.get(i, 0)) for i in range(min(left_ones), h))
                            r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, max(ones)+1))
                            # Try parsing r_str
                            w_r = r_str[::-1]
                            if w_r.startswith("100") and w_r.endswith("1"):
                                parts = w_r[3:-1].split("00")
                                if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                                    vals = [len(p)//2 for p in parts]
                                    outcome = f"KP(L={l_str};len={len(vals)-2};a={vals[-2]};b={vals[-1]})"
                                    break
                row_res.append(f"k={k}:{outcome}")
            print(f"C1={cand}: " + " | ".join(row_res))
