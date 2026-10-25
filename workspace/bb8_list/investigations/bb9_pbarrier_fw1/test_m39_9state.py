import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm(m_str):
    tr = {}
    for q, row in enumerate(m_str.split('_')):
        for c in range(2):
            cell = row[3*c:3*c+3]
            if cell[0] != '-':
                w = int(cell[0])
                d = 1 if cell[1] == 'R' else -1
                nx = ord(cell[2]) - ord('A')
                tr[(q, c)] = (w, d, nx, f"{chr(65+q)}{c}")
    return tr

def fmt_tape(tape, pos, q, lo_pad=2):
    ks = [k for k, v in tape.items() if v] + [pos]
    lo, hi = min(ks) - lo_pad, max(ks) + lo_pad
    s = []
    for i in range(lo, hi + 1):
        v = str(tape.get(i, 0))
        if i == pos:
            s.append(f"[{chr(65+q)}{v}]")
        else:
            s.append(v)
    return f"(lo={lo}) " + "".join(s)

M_NEW = '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0RH0LE_0LB1RF_---1RI_1RG---'
print("=== Testing 9-state candidate:", M_NEW, "===")
tr = parse_tm(M_NEW)
tape = {}
pos = 0
q = 0
for st in range(1, 70000):
    c = tape.get(pos, 0)
    if (q, c) not in tr:
        print(f"HALT at step {st}: {chr(65+q)}{c} {fmt_tape(tape, pos, q)}")
        break
    w_bit, d, nx, sl = tr[(q, c)]
    if sl in ('F0', 'G0', 'H0'):
        ks = [k for k, v in tape.items() if v] + [pos]
        lo, hi = min(ks), max(ks)
        s = ''.join(str(tape.get(i, 0)) for i in range(pos+1, hi+2))
        print(f"step {st:5d} (next={sl}): N={len(s)//2}, ones={sum(tape.values())}, {fmt_tape(tape, pos, q)[:80]}")
    tape[pos] = w_bit
    pos += d
    q = nx
    ks = [k for k, v in tape.items() if v]
    if q == 2 and ks and pos > max(ks) and tape.get(pos, 0) == 0:
        if st <= 100 or (56900 <= st <= 57600):
            s = ''.join(str(tape.get(i, 0)) for i in range(min(ks), pos))
            parts = [len(p) for p in s[:-1].split('0')]
            print(f"step {st:5d}: C0 end-moment! len_parts={len(parts)}, parts={parts[:8]}...{parts[-4:]} (ones={sum(tape.values())})")
