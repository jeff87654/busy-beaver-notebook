import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB".split("_")
tr = [t for row in M1 for t in (row[:3], row[3:])]

def run_tape(bits_str, h_pos, state_ch, max_steps=100000):
    tape = {i: int(c) for i, c in enumerate(bits_str)}
    h = h_pos
    s = ord(state_ch) - 65
    for step in range(1, max_steps + 1):
        b = tape.get(h, 0)
        act = tr[2 * s + b]
        if act == "---":
            mn = min(min(tape), h)
            mx = max(max(tape), h)
            out = []
            for i in range(mn, mx + 1):
                bit = str(tape.get(i, 0))
                if i == h:
                    out.append(f"[{chr(65+s)}{bit}]")
                else:
                    out.append(bit)
            return step, "".join(out)
        tape[h] = int(act[0])
        h += 1 if act[1] == "R" else -1
        s = ord(act[2]) - 65
    return -1, "TIMEOUT"

tape = {}
h = 0; s = 0
for step in range(1, 3900):
    b = tape.get(h, 0)
    act = tr[2*s + b]
    tape[h] = int(act[0])
    h += 1 if act[1] == "R" else -1
    s = ord(act[2]) - 65
    if step in (3715, 3897):
        mn, mx = min(tape), max(tape)
        bits = "".join(str(tape.get(i,0)) for i in range(mn, mx+1))
        print(f"step {step}: state={chr(65+s)} h_off={h-mn} bits={bits}")

# Now test K(0^k; a; 0) in template L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1
# From step 3897 we can see the exact layout of K(1^19, 0; 8; 0)!
for k in (1, 2, 3, 4):
    for a in (k, k+1, k+2, k+3):
        bits = "100" + "11" * a + "00" + "00" * k + "1"
        st, cfg = run_tape(bits, -1, "E")
        print(f"k={k}, a={a}: step={st} cfg={cfg}")
