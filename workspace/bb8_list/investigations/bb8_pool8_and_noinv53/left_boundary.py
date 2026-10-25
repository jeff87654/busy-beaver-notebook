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

# Decode a bitstring on the right of [E0] into symbols 0='01', 1='001'
def dec_right(s):
    out = []
    i = 0
    while i < len(s):
        if s.startswith('001', i):
            out.append('1')
            i += 3
        elif s.startswith('01', i):
            out.append('0')
            i += 2
        else:
            return "".join(out) + f"?({s[i:]})"
    return "".join(out)

# Observe every time head is at [E0] at the left record in the actual blank-tape run, decoded in {0='01', 1='001'}!
tape = {}
head = 0
q = 0
lo = 0
hi = 0

print("Left-record [E0] configurations decoded in {0='01', 1='001'}:")
cnt = 0
for step in range(1, 500001):
    c = tape.get(head, 0)
    w, d, q = trans[(q, c)]
    tape[head] = w
    head += d
    if head < lo:
        lo = head
        if q == 4: # E
            cnt += 1
            bits = "".join(str(tape.get(i, 0)) for i in range(lo + 1, hi + 1))
            dec = dec_right(bits)
            # compress runs of '10' at the right end of dec
            m = 0
            while dec.endswith('10') and len(dec) >= 2:
                dec = dec[:-2]
                m += 1
            if cnt <= 80:
                print(f"L#{cnt:3d} step={step:7d} span={hi-lo+1:4d}: [E0] {dec} (10)^{m}")
    elif head > hi:
        hi = head
