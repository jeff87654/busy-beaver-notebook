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

def fmt(tape, lo, hi, head, q):
    out = []
    for i in range(lo, hi + 1):
        b = str(tape.get(i, 0))
        if i == head:
            out.append(f"[{chr(ord('A')+q)}{b}]")
        else:
            out.append(b)
    return "".join(out)

for step in range(1, 2600):
    if 2175 <= step <= 2380:
        print(f"{step:5d}: {fmt(tape, lo, hi, head, q)}")
    c = tape.get(head, 0)
    w, d, q = trans[(q, c)]
    tape[head] = w
    head += d
    if head < lo: lo = head
    if head > hi: hi = head
