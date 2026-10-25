import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def parse_tm(s):
    tr = {}
    for st, blk in enumerate(s.split('_')):
        for bit in (0, 1):
            m = blk[bit*3:(bit+1)*3]
            if m != '---':
                tr[(st, bit)] = (int(m[0]), -1 if m[1] == 'L' else 1, ord(m[2]) - ord('A'))
    return tr

def format_tape(tape, head, state):
    if not tape:
        mn = mx = head
    else:
        mn = min(min(tape.keys()), head)
        mx = max(max(tape.keys()), head)
    out = []
    for i in range(mn, mx + 1):
        v = tape.get(i, 0)
        if i == head:
            out.append(f"{chr(ord('A')+state)}[{v}]")
        else:
            out.append(str(v))
    return "".join(out)

def make_c1_new_halt_tape(b):
    # E[1] 11 010100101 (101)^b
    cfg = "E[1]11010100101" + ("101" * b)
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    return tape, head, state

def check_c1_clean_k(tape, head, state):
    # In C1_new (and C1_bb7), canonical right-cap B[0] configuration is:
    # 11 ((01)^d 1)* (101)^b 0111001 B[0]  or similar!
    # Wait: during cascade, whenever state == 1 (B) and tape.get(head, 0) == 0 and head > max(tape.keys()):
    if state != 1 or tape.get(head, 0) != 0:
        return None
    if not tape or head <= max(tape.keys()):
        return None
    ft = format_tape(tape, head, state)
    # Match canonical K(d_k, ..., d_1; a; b):
    # Prefix: 11 (or dirty prefix), then digits, then (101)^b 0111001 B[0] or (101)^b B[0]
    m = re.match(r'^([01]*?)11((?:(?:01)*1)+?)((?:101)*)0111001B\[0\]$', ft)
    if m:
        junk = m.group(1)
        digits_s = m.group(2)
        b_new = len(m.group(3)) // 3
        ds = [len(p)//2 for p in digits_s.split('1')[:-1]]
        return ("B0_CAP", junk, ds, b_new)
    return None

if __name__ == '__main__':
    base_tm = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"
    base_tr = parse_tm(base_tm)
    moves8 = [(w, d, ns) for w in (0, 1) for d in (-1, 1) for ns in range(8)]
    e1_moves = [(w, d, 7) for w in (0, 1) for d in (-1, 1)]
    
    print("=== Scanning all 8-state extensions of C1_new ===")
    interesting = []
    for e1 in e1_moves:
        for h0 in [None] + moves8:
            for h1 in [None] + moves8:
                tr = dict(base_tr)
                tr[(4, 1)] = e1
                if h0 is not None: tr[(7, 0)] = h0
                if h1 is not None: tr[(7, 1)] = h1
                
                # Simulate on b = 4 up to 2000 steps
                tape, head, state = make_c1_new_halt_tape(4)
                b0_hits = []
                status = "RUN"
                for step in range(1, 2001):
                    v = tape.get(head, 0)
                    t = tr.get((state, v))
                    if t is None:
                        status = f"HALT(s={step-1},ones={len(tape)})"
                        break
                    w, d, ns = t
                    if w == 0: tape.pop(head, None)
                    else: tape[head] = 1
                    head += d; state = ns
                    if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
                        ft = format_tape(tape, head, state)
                        b0_hits.append((step, len(tape), ft))
                        if len(b0_hits) >= 4:
                            break
                if len(b0_hits) >= 2:
                    # Check if b=5 gives a larger list or larger b!
                    tape5, head5, state5 = make_c1_new_halt_tape(5)
                    b0_hits5 = []
                    for step in range(1, 2001):
                        v = tape5.get(head5, 0)
                        t = tr.get((state5, v))
                        if t is None: break
                        w, d, ns = t
                        if w == 0: tape5.pop(head5, None)
                        else: tape5[head5] = 1
                        head5 += d; state5 = ns
                        if state5 == 1 and tape5.get(head5, 0) == 0 and tape5 and head5 > max(tape5.keys()):
                            b0_hits5.append((step, len(tape5), format_tape(tape5, head5, state5)))
                            if len(b0_hits5) >= 4: break
                    if b0_hits5 and b0_hits5[0][2] != b0_hits[0][2]:
                        def fmt_mv(mv):
                            if mv is None: return "---"
                            return f"{mv[0]}{'L' if mv[1]==-1 else 'R'}{chr(ord('A')+mv[2])}"
                        lbl = f"E1={fmt_mv(e1)} H0={fmt_mv(h0)} H1={fmt_mv(h1)}"
                        interesting.append((lbl, b0_hits[0], b0_hits5[0]))
    print(f"Found {len(interesting)} b-dependent B[0] right-cap rebuilders on C1_new:")
    for lbl, h4, h5 in interesting[:40]:
        print(f"  {lbl}:")
        print(f"    b=4: step={h4[0]:4d} {h4[2]}")
        print(f"    b=5: step={h5[0]:4d} {h5[2]}")
