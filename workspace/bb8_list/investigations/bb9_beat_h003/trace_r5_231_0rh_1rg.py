import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tr(M):
    tr = []
    for row in M.split('_'):
        for b in (0, 1):
            s = row[3*b : 3*b+3]
            if s[0] == '-' or s[2] == '-':
                tr.append((-1, 0, -1))
            else:
                tr.append((int(s[0]), 1 if s[1] == 'R' else -1, ord(s[2]) - 65))
    return tr

def test_regime2_right_end(U=53, m_zeros=2, left_1100=15):
    M = '1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RG'
    tr = parse_tr(M)
    OFFSET = 10000
    tape = bytearray(100000)
    # In Regime II: (1100)^left_1100 [E>0] 100 1^U (00)^(m_zeros+1) 1 0^inf
    pos = OFFSET
    for _ in range(left_1100):
        tape[pos] = 1; tape[pos+1] = 1; tape[pos+2] = 0; tape[pos+3] = 0
        pos += 4
    h = pos
    tape[pos] = 0; tape[pos+1] = 1; tape[pos+2] = 0; tape[pos+3] = 0
    pos += 4
    for _ in range(U):
        tape[pos] = 1; pos += 1
    for _ in range(2 * (m_zeros + 1)):
        tape[pos] = 0; pos += 1
    tape[pos] = 1
    lo = OFFSET
    hi = pos
    q = 4
    for step in range(1, 50000):
        b = tape[h]
        act = tr[2 * q + b]
        if act[0] == -1:
            print(f"U={U}, m_zeros={m_zeros}: HALT at {chr(65+q)}{b} at step {step}!")
            return
        tape[h] = act[0]
        if h < lo and act[0] == 1: lo = h
        if h > hi and act[0] == 1: hi = h
        h += act[1]
        q = act[2]
        if q == 4 and tape[h] == 0 and tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0 and (h - OFFSET) % 4 == 0:
            k_rem = (h - OFFSET) // 4
            p = h + 4
            blocks = []
            ok = True
            while p <= hi - 1:
                ones = 0
                while p <= hi - 1 and tape[p] == 1: ones += 1; p += 1
                if p + 1 <= hi - 1 and tape[p] == 0 and tape[p+1] == 0:
                    blocks.append(ones); p += 2
                else:
                    ok = False; break
            if ok and tape[hi] == 1:
                print(f"  step {step:5d}: k_rem={k_rem:2d} (used {left_1100-k_rem:2d}) -> [E0] 100 blocks={blocks[:12]} (len={len(blocks)})")
                return

for m_zeros in [1, 2, 3, 4, 5]:
    print(f"--- Testing m_zeros = {m_zeros} (with 100 after [E0]) ---")
    test_regime2_right_end(U=53, m_zeros=m_zeros, left_1100=15)
