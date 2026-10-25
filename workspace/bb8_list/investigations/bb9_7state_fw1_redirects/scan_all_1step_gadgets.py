import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def parse_tm(tm):
    tr = {}
    free_slots = []
    for q, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] == '-':
                free_slots.append((q, c))
            else:
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), d, ord(x[2]) - 65)
    return tr, free_slots

def trace_transitions(tm, tape_init, pos_init, q_init, max_steps):
    tr, _ = parse_tm(tm)
    tape = dict(tape_init)
    pos = pos_init
    q = q_init
    prev_slot = "START"
    events = set()
    for step in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        cur_slot = chr(65 + q) + str(c)
        b_left = tape.get(pos - 1, 0)
        b_right = tape.get(pos + 1, 0)
        b_l2 = tape.get(pos - 2, 0)
        b_r2 = tape.get(pos + 2, 0)
        events.add((prev_slot, cur_slot, b_left, b_right, b_l2, b_r2))
        if (q, c) not in tr:
            break
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
        prev_slot = cur_slot
    return events

def trace_k_trans(tm, t_str, B0, ds, a, maxs=400000):
    t = kl.tmpl(tm, t_str)
    evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=100, T=t, pall=1)
    stop_step = maxs
    ev1 = ('END',)
    for e in evs[1:]:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B0 and e[2] != ds):
            ev1 = e
            stop_step = e[1]
            break
    mir = (t['o'] == 'L')
    w = kl.word(t, ds, a, B0)
    tape = {}
    if not mir:
        for i, ch in enumerate(w):
            if ch == '1': tape[i] = 1
        pos = len(w)
    else:
        for i, ch in enumerate(w):
            if ch == '1': tape[-i] = 1
        pos = -len(w)
    q = ord(t['q']) - 65
    return ev1, trace_transitions(tm, tape, pos, q, stop_step)

def build_9state_gadget(tm, prev_slot, cur_slot, d_insp, b_halt):
    tr, free_slots = parse_tm(tm)
    q_free, b_free = free_slots[0]
    p_q, p_c = ord(prev_slot[0]) - 65, int(prev_slot[1])
    c_q, c_c = ord(cur_slot[0]) - 65, int(cur_slot[1])
    w_prev, dir_prev, _ = tr[(p_q, p_c)]
    # Copy base machine into 9 states (A..I)
    rows = [list(row) for row in (tm + "_------_------").split('_')]
    def set_slot(q, c, w, d, nq):
        s = "---" if w < 0 else f"{w}{'R' if d > 0 else 'L'}{chr(65 + nq)}"
        rows[q][3*c:3*c+3] = list(s)
    # 1. Redirect prev_slot to H (7)
    set_slot(p_q, p_c, w_prev, dir_prev, 7)
    # 2. H[1 - c_c] copies c_q[1 - c_c]
    if (c_q, 1 - c_c) in tr:
        w_o, d_o, nq_o = tr[(c_q, 1 - c_c)]
        set_slot(7, 1 - c_c, w_o, d_o, nq_o)
    # 3. H[c_c] writes b_free and steps d_insp to I (8)
    set_slot(7, c_c, b_free, d_insp, 8)
    # 4. I[b_halt] = ---, I[1 - b_halt] writes 1 - b_halt and steps -d_insp to q_free
    set_slot(8, b_halt, -1, 0, 0)
    set_slot(8, 1 - b_halt, 1 - b_halt, -d_insp, q_free)
    # 5. free_slot (q_free, b_free) copies c_q[c_c]
    w_c, d_c, nq_c = tr[(c_q, c_c)]
    set_slot(q_free, b_free, w_c, d_c, nq_c)
    return "_".join("".join(r) for r in rows)

# Check reb_E2 and reb_E1_1..9
if __name__ == '__main__':
    print("=== Scanning reb_E2 and reb_E1_1..9 for 1-step (r=1) and 2-step (r=2) transition-resolved contexts ===")
E_CANDS = [
    ("reb_E2", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 415,
     [[5,4], [5,2], [5,4,0], [5,4,0,0], [5,0,0], [3,0,0]],
     [[1,0,0], [1,0,0,0], [1,0,0,0,0,0]]),
    ("reb_E1_1", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1493,
     [[1,4], [1,2], [1,4,0], [1,4,0,0], [1,3,0], [1,3,0,0], [1,2,1], [1,2,1,0], [1,0,1]],
     [[1,0,0,1], [1,0,0,0,1], [1,0,0], [1,0,0,0]]),
    ("reb_E1_2", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RC0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500,
     [[1,4], [1,2], [1,4,0], [1,4,0,0], [1,3,0], [1,3,0,0], [1,2,1], [1,2,1,0], [1,0,1]],
     [[1,0,0,1], [1,0,0,0,1], [1,0,0], [1,0,0,0]]),
    ("reb_E1_6", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RE0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500,
     [[1,4], [1,2], [1,4,0], [1,4,0,0], [1,3,0], [1,3,0,0], [1,2,1], [1,2,1,0], [1,0,1]],
     [[1,0,0,1], [1,0,0,0,1], [1,0,0], [1,0,0,0]]),
    ("reb_E1_7", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RF0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500,
     [[1,4], [1,2], [1,4,0], [1,4,0,0], [1,3,0], [1,3,0,0], [1,2,1], [1,2,1,0], [1,0,1]],
     [[1,0,0,1], [1,0,0,0,1], [1,0,0], [1,0,0,0]]),
    ("reb_E1_8", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RF0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, 1500,
     [[1,4], [1,2], [1,4,0], [1,4,0,0], [1,3,0], [1,3,0,0], [1,2,1], [1,2,1,0], [1,0,1]],
     [[1,0,0,1], [1,0,0,0,1], [1,0,0], [1,0,0,0]]),
]

for name, tm, t_str, B0, init_st, db_list, e_list in E_CANDS:
    base_ev = trace_transitions(tm, {}, 0, 0, init_st)
    for ds in db_list:
        for a in [5, 7, 9]:
            _, evs = trace_k_trans(tm, t_str, B0, ds, a)
            base_ev |= evs
    e_common = None
    for ds in e_list:
        for a in [7, 9]:
            _, evs = trace_k_trans(tm, t_str, B0, ds, a)
            e_common = set(evs) if e_common is None else (e_common & evs)

    # Check 1-step neighbor (b_left or b_right) given (prev_slot, cur_slot)
    base_L = {(p, c, bl) for (p, c, bl, br, bl2, br2) in base_ev}
    base_R = {(p, c, br) for (p, c, bl, br, bl2, br2) in base_ev}
    e_L = {(p, c, bl) for (p, c, bl, br, bl2, br2) in e_common}
    e_R = {(p, c, br) for (p, c, bl, br, bl2, br2) in e_common}
    diff_L = sorted(e_L - base_L)
    diff_R = sorted(e_R - base_R)
    print(f"\n--- {name}: diff_L={len(diff_L)}, diff_R={len(diff_R)} ---")
    for p, c, bl in diff_L:
        tm9 = build_9state_gadget(tm, p, c, -1, bl)
        print(f"  [L-neighbor] prev={p} -> cur={c}, b_left={bl} => {tm9}")
    for p, c, br in diff_R:
        tm9 = build_9state_gadget(tm, p, c, +1, br)
        print(f"  [R-neighbor] prev={p} -> cur={c}, b_right={br} => {tm9}")
