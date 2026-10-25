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
            return None
    return "".join(out)

def parse_ternary(w):
    # w is a string in {0, 1}* after '00101' and before (10)^m
    # digits: d0 = '001', d1 = '01', d2 = '1'
    digs = []
    i = 0
    while i < len(w):
        if w.startswith('001', i):
            digs.append(0)
            i += 3
        elif w.startswith('01', i):
            digs.append(1)
            i += 2
        elif w.startswith('1', i):
            digs.append(2)
            i += 1
        else:
            return None
    return digs

tape = {}
head = 0
q = 0
lo = 0
hi = 0

kmoments = []
for step in range(1, 5000001):
    c = tape.get(head, 0)
    w, d, q = trans[(q, c)]
    tape[head] = w
    head += d
    if head < lo:
        lo = head
        if q == 4: # E
            bits = "".join(str(tape.get(i, 0)) for i in range(lo + 1, hi + 1))
            dec = dec_right(bits)
            if dec and dec.startswith('00101'):
                body = dec[5:]
                m = 0
                while body.endswith('10') and len(body) >= 2:
                    body = body[:-2]
                    m += 1
                # Wait: if the last ternary digit is d1='01' or d2='1' preceded by '0', '10' might eat into the ternary digits!
                # Let's check: in L#5, dec = 0010101 (10)^1, body='01', m=1.
                kmoments.append((step, hi - lo + 1, dec))
    elif head > hi:
        hi = head

print(f"Total clean [E0] moments in 5,000,000 steps: {len(kmoments)}")
for idx, (step, span, dec) in enumerate(kmoments[:45]):
    # Know that each full carry block has k digits
    print(f"K#{idx:3d} step={step:8d} span={span:4d}: {dec[:40]}" + (f"... (len {len(dec)})" if len(dec) > 40 else ""))
