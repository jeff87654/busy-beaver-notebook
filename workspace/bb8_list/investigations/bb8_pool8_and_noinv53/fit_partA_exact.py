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

def parse_all(bits):
    # Header is '010100101001' (12 bits = '00101' in {0='01', 1='001'})
    if not bits.startswith('010100101001'):
        return None
    rest = bits[12:]
    # Now parse digits from left to right:
    # d0 = '0101001' (7 bits)
    # d1 = '01001'   (5 bits)
    # d2 = '001'     (3 bits)
    # G  = '01010001' (8 bits, carry marker gamma!)
    # Wait: tail is '00101'^m, where '00101' = d2 + '01'!
    # Notice that if we strip '00101' from the right FIRST:
    # Every tail unit is '00101' (5 bits).
    # Wait: can any digit d0, d1, d2, G end in '00101'?
    # No! Every digit d0 ('0101001'), d1 ('01001'), d2 ('001'), G ('01010001') ends in '001'!
    # Whereas the tail block '00101' ends in '101'!
    # WAIT A SECOND!
    # Every digit (d0, d1, d2, G) ends in '001' (or '0001'), NEVER '101'!
    # And every tail block '00101' ends in '101'!
    # So the boundary between the digit list and the tail ('00101')^m is 100% UNAMBIGUOUS!
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

records = []
for step in range(1, 10000001):
    c = tape.get(head, 0)
    w, d, q = trans[(q, c)]
    tape[head] = w
    head += d
    if head < lo:
        lo = head
        if q == 4: # E
            bits = "".join(str(tape.get(i, 0)) for i in range(lo + 1, hi + 1))
            p = parse_all(bits)
            records.append((step, hi - lo + 1, p, bits[:30]))
    elif head > hi:
        hi = head

print(f"Total [E0] left records in 10,000,000 steps: {len(records)}")
bad = [r for r in records if r[2] is None or (isinstance(r[2], tuple) and len(r[2]) > 0 and r[2][0] == 'BAD')]
print(f"Unparsed records (after initial 4 startup records): {[r[:3] for r in bad]}")
for idx, (step, span, p, _) in enumerate(records[:65]):
    print(f"L#{idx+1:3d} step={step:8d} span={span:4d}: {p}")
