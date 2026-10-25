import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

m_str = "1RB0LE_0RC1LF_1LD0RD_0LA---_1LA1RG_1RB1RF_0RH0LG_1RE1LD"
states = m_str.split('_')
trans = {}
for q, st in enumerate(states):
    for s in (0, 1):
        sub = st[3*s:3*s+3]
        if sub == '---':
            trans[(q, s)] = None
        else:
            w = int(sub[0])
            d = 1 if sub[1] == 'R' else -1
            nx = ord(sub[2]) - ord('A')
            trans[(q, s)] = (w, d, nx)

tape = {}
head = 0
q = 0
lo = 0
hi = 0
used = set()

def fmt_tape(tape, lo, hi, head, q):
    s = []
    for i in range(lo, hi + 1):
        bit = str(tape.get(i, 0))
        if i == head:
            s.append(f"[{chr(ord('A')+q)}{bit}]")
        else:
            s.append(bit)
    return "".join(s)

def rle_blocks(bits, k):
    # group into blocks of length k from left or right
    out = []
    for i in range(0, len(bits), k):
        blk = bits[i:i+k]
        if out and out[-1][0] == blk:
            out[-1][1] += 1
        else:
            out.append([blk, 1])
    return " ".join(f"{b}^{n}" if n > 1 else b for b, n in out)

print("Tracing first 200,000 steps at left/right records:")
rec_count = 0
for step in range(1, 500001):
    c = tape.get(head, 0)
    used.add((q, c))
    t = trans[(q, c)]
    if t is None:
        print(f"HALT at step {step}")
        break
    w, d, q = t
    tape[head] = w
    head += d
    is_lo = head < lo
    is_hi = head > hi
    if is_lo:
        lo = head
    if is_hi:
        hi = head
    if (is_lo or is_hi) and (rec_count < 80 or step > 400000):
        rec_count += 1
        side = "L" if is_lo else "R"
        span = hi - lo + 1
        if span <= 120:
            print(f"step={step:7d} ({side}) span={span:3d}: {fmt_tape(tape, lo, hi, head, q)}")
        else:
            bits = "".join(str(tape.get(i, 0)) for i in range(lo, hi + 1))
            print(f"step={step:7d} ({side}) q={chr(ord('A')+q)} span={span:4d} RLE5_L: {rle_blocks(bits, 5)[:120]}")

print("\nUsed transitions in 500,000 steps:")
all_tr = [(q, s) for q in range(8) for s in (0, 1)]
for q_i, s_i in all_tr:
    nm = f"{chr(ord('A')+q_i)}{s_i}"
    print(f"  {nm}: {'USED' if (q_i, s_i) in used else 'UNUSED'} ({states[q_i][3*s_i:3*s_i+3]})")
