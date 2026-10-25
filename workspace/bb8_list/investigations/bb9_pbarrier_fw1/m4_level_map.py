import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

M4 = "1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_1RA1RE"

def parse_tm(m_str, mirror=False):
    tr = {}
    for q, row in enumerate(m_str.split('_')):
        for c in range(2):
            cell = row[3*c:3*c+3]
            if cell[0] != '-':
                w = int(cell[0])
                d = 1 if cell[1] == 'R' else -1
                if mirror:
                    d = -d
                nx = ord(cell[2]) - ord('A')
                tr[(q, c)] = (w, d, nx, f"{chr(65+q)}{c}")
    return tr

def decode_m4(tape, pos):
    ks = [k for k, v in tape.items() if v]
    if not ks:
        return None
    lo = min(ks)
    s = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
    # Expected format: '1' + ''.join('01'*x + '0' for x in ds + [a]) + '01'*b
    # Wait: let's parse from right to left or left to right!
    if not s.startswith('1'):
        return ('RAW', s)
    rem = s[1:]
    # From right: '01'*b, preceded by '0' (unless rem is empty, as at step 5 where s='1')
    if rem == '':
        return ([], 0, 0, s)
    # Count trailing '01's after the last '00' or start
    # Actually every digit x in ds+[a] is '01'*x + '0'.
    # Notice '01'*x + '0' always ends with '0', whereas '01'*b ends with '1' (if b>0) or '' (if b=0).
    b = 0
    while rem.endswith('01'):
        b += 1
        rem = rem[:-2]
    # Now rem must be ''.join('01'*x + '0' for x in ds + [a])
    items = []
    idx = 0
    while idx < len(rem):
        x = 0
        while rem[idx:idx+2] == '01':
            x += 1
            idx += 2
        if idx < len(rem) and rem[idx] == '0':
            idx += 1
            items.append(x)
        else:
            return ('BAD', s, rem[idx:])
    if not items:
        return ([], 0, b, s)
    return (items[:-1], items[-1], b, s)

tr = parse_tm(M4, True)
tape = {}
pos = 0
q = 0
for st in range(1, 3000):
    c = tape.get(pos, 0)
    w_bit, d, nx, sl = tr[(q, c)]
    if sl == 'G0':
        ks = [k for k, v in tape.items() if v]
        lo, hi = min(ks), max(ks)
        s = ''.join(str(tape.get(i, 0)) for i in range(pos, hi+1))
        print(f"step {st:4d}: G0 reached! tape_from_pos = {s[:30]}... (len={len(s)}, N={(len(s)-2)//3})")
    tape[pos] = w_bit
    pos += d
    q = nx
    ks = [k for k, v in tape.items() if v]
    if q == 2 and ks and pos > max(ks) and tape.get(pos, 0) == 0:
        dec = decode_m4(tape, pos)
        if dec[0] in ('RAW', 'BAD'):
            print(f"step {st:4d}: {dec}")
        else:
            ds, a, b, s = dec
            if b == 1 or len(ds) == 0 or st in (5, 51, 373, 2799):
                print(f"step {st:4d}: K(ds={ds}; a={a}; b={b})")
