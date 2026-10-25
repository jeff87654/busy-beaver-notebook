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

def parse_record(bits):
    if not bits.startswith('010100101001'):
        return None
    rest = bits[12:]
    m = 0
    while rest.endswith('00101'):
        rest = rest[:-5]
        m += 1
    digs = []
    i = 0
    while i < len(rest):
        if rest.startswith('01010001', i):
            digs.append('G')
            i += 8
        elif rest == '01010' + rest[i+5:] and i + 5 == len(rest):
            digs.append('G_top')
            i += 5
        elif rest.startswith('0101001', i):
            digs.append(0)
            i += 7
        elif rest.startswith('01001', i):
            digs.append(1)
            i += 5
        elif rest.startswith('001', i):
            digs.append(2)
            i += 3
        else:
            return ('BAD', rest[i:], digs, m)
    return (tuple(digs), m)

tape = {}
head = 0
q = 0
lo = 0
hi = 0

clean_k = []
all_recs = []
for step in range(1, 20000001):
    c = tape.get(head, 0)
    w, d, q = trans[(q, c)]
    tape[head] = w
    head += d
    if head < lo:
        lo = head
        if q == 4:
            bits = "".join(str(tape.get(i, 0)) for i in range(lo + 1, hi + 1))
            p = parse_record(bits)
            all_recs.append((step, hi - lo + 1, p))
            if p and p[0] != 'BAD' and all(isinstance(x, int) for x in p[0]):
                clean_k.append((step, hi - lo + 1, p[0], p[1]))
    elif head > hi:
        hi = head

bad = [r for r in all_recs[4:] if r[2] is None or r[2][0] == 'BAD']
print(f"Total records after L#4: {len(all_recs)-4}, BAD: {len(bad)}")
print(f"Total clean digit-only K-moments: {len(clean_k)}")

# Verify transitions between consecutive clean digit-only K-moments!
mismatches = 0
for i in range(len(clean_k) - 1):
    st1, sp1, d1, m1 = clean_k[i]
    st2, sp2, d2, m2 = clean_k[i+1]
    # Predict (d2, m2) from (d1, m1)
    d = list(d1)
    if d[0] in (0, 1):
        d[0] += 1
        pred_d, pred_m = tuple(d), m1 + 2
    else:
        # count leading 2s
        r = 0
        while r < len(d) and d[r] == 2:
            r += 1
        if r == 1 and len(d) >= 2:
            d[0] = 0
            d[1] += 1
            pred_d, pred_m = tuple(d), m1
        elif r < len(d):
            # r >= 2, carry stops at d[r] < 2
            for j in range(r):
                d[j] = 0
            d[0] = 1
            d[r] += 1
            pred_d, pred_m = tuple(d), m1
        else:
            # r == len(d): all digits are 2!
            # Wait: let's see what (2^k, m) transitions to!
            pred_d, pred_m = None, None
    if pred_d is not None and (pred_d != d2 or pred_m != m2):
        print(f"MISMATCH at K#{i}: {(d1, m1)} -> {(d2, m2)}, expected {(pred_d, pred_m)}")
        mismatches += 1
    elif pred_d is None:
        print(f"OVERFLOW at K#{i} (k={len(d1)}): {(d1, m1)} -> {(d2, m2)} (dt={st2-st1})")

print(f"Non-overflow mismatches: {mismatches}")
