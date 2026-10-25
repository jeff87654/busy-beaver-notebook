import sys
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

def make_c4_halt_tape(k, M):
    cfg = ("10" * (2*k - 3)) + "11001C[1]1" + ("0011" * M) + "001"
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

def test_context2():
    for name, base_tm in [
        ("C4_1", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"),
        ("C4_2", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"),
    ]:
        print(f"=== {name} ===")
        base_tr = parse_tm(base_tm)
        moves8 = [(w, d, ns) for w in (0, 1) for d in (-1, 1) for ns in range(8)]
        c1_moves = [(w, d, 7) for w in (0, 1) for d in (-1, 1)]
        
        context2_hits = []
        for c1 in c1_moves:
            for h0 in moves8:
                for h1 in moves8:
                    tr = dict(base_tr)
                    tr[(2, 1)] = c1
                    tr[(7, 0)] = h0
                    tr[(7, 1)] = h1
                    
                    tape, head, state = make_c4_halt_tape(5, 4)
                    last_h_step = 0
                    reentered_c1 = None
                    used_slots_phase1 = set()
                    for step in range(1, 5000):
                        v = tape.get(head, 0)
                        if (state, v) in ((2, 1), (7, 0), (7, 1)):
                            if step - last_h_step > 200:
                                reentered_c1 = (step, last_h_step, format_tape(tape, head, state), set(used_slots_phase1))
                                break
                            last_h_step = step
                            used_slots_phase1.add((state, v))
                        w, d, ns = tr[(state, v)]
                        if w == 0: tape.pop(head, None)
                        else: tape[head] = 1
                        head += d; state = ns
                    if reentered_c1:
                        context2_hits.append((c1, h0, h1, reentered_c1))
        print(f"Found {len(context2_hits)} 8-state machines that enter Round-2 cascade (>200 base steps) on k=5, M=4 and then re-enter C1:")
        seen_cfgs = set()
        for c1, h0, h1, (step, last_h, ft, used1) in context2_hits:
            if ft not in seen_cfgs:
                seen_cfgs.add(ft)
                def fm(mv): return f"{mv[0]}{'L' if mv[1]==-1 else 'R'}{chr(ord('A')+mv[2])}"
                print(f"  C1={fm(c1)} H0={fm(h0)} H1={fm(h1)}: last_H={last_h}, reenter_C1={step}, used1={len(used1)}")
                print(f"    {ft[:100]}")

if __name__ == '__main__':
    test_context2()
