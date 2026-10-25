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
            trans[(q, s)] = (int(sub[0]), 1 if sub[1] == 'R' else -1, ord(sub[2]) - ord('A'))

tape = {}
head = 0
q = 0
lo = 0
hi = 0

def rle5_from_right(bits):
    rem = len(bits) % 5
    pre = bits[:rem] if rem else ""
    out = []
    for i in range(rem, len(bits), 5):
        blk = bits[i:i+5]
        if out and out[-1][0] == blk:
            out[-1][1] += 1
        else:
            out.append([blk, 1])
    s = " ".join(f"{b}^{n}" if n > 1 else b for b, n in out)
    return (f"({pre}) " if pre else "") + s

print("Left records [E0] (head at new lo in state E):")
cnt = 0
for step in range(1, 2000001):
    c = tape.get(head, 0)
    w, d, q = trans[(q, c)]
    tape[head] = w
    head += d
    if head < lo:
        lo = head
        if q == 4: # E
            cnt += 1
            bits = "".join(str(tape.get(i, 0)) for i in range(lo + 1, hi + 1))
            if cnt <= 60 or cnt % 20 == 0:
                print(f"L#{cnt:3d} step={step:8d} len={len(bits):4d}: [E0] {rle5_from_right(bits)}")
    elif head > hi:
        hi = head
