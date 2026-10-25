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

def make_exhaustion_tape(k, M):
    cfg = ('10' * (2*k - 3)) + '11001C[1]1' + ('0011' * M) + '001'
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

def check_valid_odd_k(tape, head, state):
    if state != 4 or tape.get(head, 0) != 0:
        return None
    if tape and head > min(tape.keys()):
        return None
    ft = format_tape(tape, head, state)
    m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
    if not m:
        return None
    b_new = len(m.group(1))
    if b_new % 2 == 0:
        return None
    ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
    if not ds or all(d == 0 for d in ds):
        return None
    z = 0
    while z < len(ds) and ds[z] == 0:
        z += 1
    if b_new < 2 * z - 1:
        return None
    return (b_new, ds)

def run_fixed_tm(tr, k, M, max_steps=10000):
    tape, head, state = make_exhaustion_tape(k, M)
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        t = tr.get((state, v))
        if t is None:
            return ("HALT", step - 1, len(tape), f"{chr(ord('A')+state)}{v}", format_tape(tape, head, state)[:80])
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
        if state == 4 and tape.get(head, 0) == 0:
            vok = check_valid_odd_k(tape, head, state)
            if vok is not None:
                return ("VALID_ODD_K", step, vok[0], vok[1])
    return ("TIMEOUT", max_steps, len(tape))

def search_base(bname, g0_str):
    base_tm = f"1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_{g0_str}"
    base_tr = parse_tm(base_tm)
    
    all_moves_9 = [(w, d, ns) for w in (0, 1) for d in (-1, 1) for ns in range(9)]
    c1_moves = [(w, d, 7) for w in (0, 1) for d in (-1, 1)]
    
    survivors = []
    nodes_visited = [0]
    
    def backtrack(tr, assigned_slots, tape, head, state, step):
        nodes_visited[0] += 1
        while step <= 850:
            v = tape.get(head, 0)
            if state == 4 and v == 0:
                vok = check_valid_odd_k(tape, head, state)
                if vok is not None:
                    survivors.append((dict(tr), list(assigned_slots), step, vok[0], vok[1]))
                    return
            key = (state, v)
            if key in tr:
                w, d, ns = tr[key]
                if w == 0: tape.pop(head, None)
                else: tape[head] = 1
                head += d; state = ns
                step += 1
            else:
                if len(assigned_slots) >= 4:
                    return
                if key == (2, 1):
                    cand_moves = c1_moves
                else:
                    # Canonicalize: don't allow jumping to state I (8) if we never reach I, wait:
                    # jumping to state I (8) is ALWAYS allowed, and if neither H0 nor H1 jumps to I,
                    # then I is simply unused (an 8-state machine).
                    cand_moves = all_moves_9
                for mv in cand_moves:
                    tr[key] = mv
                    assigned_slots.append(key)
                    t_copy = dict(tape)
                    w, d, ns = mv
                    if w == 0: t_copy.pop(head, None)
                    else: t_copy[head] = 1
                    backtrack(tr, assigned_slots, t_copy, head + d, ns, step + 1)
                    assigned_slots.pop()
                    del tr[key]
                return

    tape0, head0, state0 = make_exhaustion_tape(k=3, M=4)
    backtrack(dict(base_tr), [], tape0, head0, state0, 1)
    print(f"[{bname}] Backtracking visited {nodes_visited[0]} nodes, found {len(survivors)} k=3 VALID_ODD_K branches.")
    
    good_21 = []
    for tr, slots, s3, b3, ds3 in survivors:
        r3_m5 = run_fixed_tm(tr, k=3, M=5, max_steps=1200)
        if r3_m5[0] != "VALID_ODD_K" or r3_m5[3] != ds3 + [1]:
            continue
        r21 = run_fixed_tm(tr, k=21, M=4, max_steps=15000)
        if r21[0] != "VALID_ODD_K":
            continue
        r21_m5 = run_fixed_tm(tr, k=21, M=5, max_steps=15000)
        if r21_m5[0] != "VALID_ODD_K" or r21_m5[3] != r21[3] + [1]:
            continue
        good_21.append((tr, slots, (s3, b3, ds3), (r21[1], r21[2], r21[3])))
    print(f"[{bname}] {len(good_21)} branches also reach VALID_ODD_K at k=21 (with M-extension).")
    
    halting_hits = []
    for tr, slots, info3, info21 in good_21:
        r4 = run_fixed_tm(tr, k=4, M=4, max_steps=80000)
        r6 = run_fixed_tm(tr, k=6, M=4, max_steps=80000)
        if r4[0] == "HALT" or r6[0] == "HALT":
            r2 = run_fixed_tm(tr, k=2, M=4, max_steps=80000)
            r5 = run_fixed_tm(tr, k=5, M=4, max_steps=5000)
            r20 = run_fixed_tm(tr, k=20, M=4, max_steps=80000)
            halting_hits.append((tr, slots, info3, info21, r2, r4, r5, r6, r20))
    print(f"[{bname}] Found {len(halting_hits)} 9-state machines that reach VALID_ODD_K on k=3,21 and HALT on k=4 or k=6!!")
    
    # Group by (info21, r4[:2], r6[:2], r20[:2])
    seen = {}
    for item in halting_hits:
        tr, slots, info3, info21, r2, r4, r5, r6, r20 = item
        sig = (info21[1], tuple(info21[2]), r4[0], r4[1], r6[0], r6[1], r20[0], r20[1])
        seen.setdefault(sig, []).append(item)
    print(f"[{bname}] Grouped into {len(seen)} distinct halting behavior classes:")
    for sig, items in seen.items():
        tr, slots, info3, info21, r2, r4, r5, r6, r20 = items[0]
        slot_str = " ".join(f"{chr(ord('A')+k[0])}{k[1]}={tr[k][0]}{'L' if tr[k][1]==-1 else 'R'}{chr(ord('A')+tr[k][2])}" for k in slots)
        c_21 = len(info21[2]) - 4
        print(f"  [{len(items):2d} machines] {slot_str}")
        print(f"    k=21: VALID_ODD_K step={info21[0]}, B={info21[1]}, ds_21={info21[2]} (c_21={c_21}, k2=M1+{c_21} is {'EVEN' if c_21%2==0 else 'ODD'})")
        print(f"    k= 3: VALID_ODD_K step={info3[0]}, B={info3[1]}, ds_3={info3[2]}")
        print(f"    k= 5: {r5[:4]}")
        print(f"    k= 2: {r2[:4]}")
        print(f"    k= 4: {r4}")
        print(f"    k= 6: {r6}")
        print(f"    k=20: {r20}")

if __name__ == '__main__':
    search_base("C4_1", "0LD0RB")
    search_base("C4_2", "1LC0RB")
