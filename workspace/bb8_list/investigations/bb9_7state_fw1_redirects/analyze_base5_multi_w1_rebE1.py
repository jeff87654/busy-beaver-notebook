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

print("=== 1. Corrected reb_E1 scan (without [1, 0, 1] in db_list!) ===")
for idx, tm in enumerate([
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RC0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RC0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RD0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RD0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RE0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RF0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RF0RG_---0RB",
    "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_0RG0RG_---0RB",
], 1):
    t_str = "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
    base_ev = trace_transitions(tm, {}, 0, 0, 1500)
    for ds in [[1,4], [1,2], [1,4,0], [1,4,0,0], [1,2,3,0], [1,2,1,0], [1,2,0,1], [1,2,0,0,1]]:
        for a in [3, 5, 9]:
            _, evs = trace_k_trans(tm, t_str, 1, ds, a)
            base_ev |= evs
    e_common = None
    for ds in [[1,0,0,1], [1,0,0,0,1], [1,0,0,0,0,1]]:
        for a in [7, 9]:
            _, evs = trace_k_trans(tm, t_str, 1, ds, a)
            e_common = set(evs) if e_common is None else (e_common & evs)
    diff_1 = sorted({(p, c, bl, br) for (p, c, bl, br, _, _) in e_common} - {(p, c, bl, br) for (p, c, bl, br, _, _) in base_ev})
    diff_2 = sorted(e_common - base_ev)
    print(f"  reb_E1_{idx}: r=1 diff={len(diff_1)}, r=2 diff={len(diff_2)}")
    for x in diff_1[:5]:
        print("    r=1:", x)
    for x in diff_2[:5]:
        print("    r=2:", x)

print("\n=== 2. Base-5 12-digit Rebuilder (c00192 / c00194) Context & Slot Analysis ===")
# Word format from parent message: A0 at left end of reversed word w with parts = [len(p) for p in w.split('0')]
# Wait: let's trace blank tape of 1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG up to step 1000
# and find exact K-moments where A0 is at the left end (or right end on unmirrored tape)!
tm_b5_1 = "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"
tm_b5_2 = "1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"

def make_b5_tape(parts):
    # When A0 is at the left end of reversed word w, on the real unmirrored tape:
    # Let's check which side A0 is on at step 9 ([3]), step 212 ([25]), step 799 ([3, 2^10, 20])!
    pass

tr_b5, _ = parse_tm(tm_b5_1)
tape = {}
pos = 0
q = 0
for st in range(1, 850):
    c = tape.get(pos, 0)
    if st in (9, 24, 99, 212, 799, 800, 815):
        mn = min(min(tape.keys(), default=0), pos)
        mx = max(max(tape.keys(), default=0), pos)
        s = "".join(f"[{chr(65+q)}{tape.get(i,0)}]" if i == pos else str(tape.get(i,0)) for i in range(mn, mx+1))
        print(f"  step {st:4d}: {s}")
    w, d, nq = tr_b5[(q, c)]
    if w: tape[pos] = 1
    else: tape.pop(pos, None)
    pos += d
    q = nq

print("\n=== 3. Audit the 3 MULTI? machines in c00206..c00207 ===")
MULTI_Q = [
    ("multi_q1", "1RB1LC_0LA---_1RD0LG_1LG0RE_1LF0LB_1RC0LE_0LA0RF", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0"),
    ("multi_q2", "1RB1LC_0LA0RF_1RD0LB_1LB0RE_1LF0LG_1RC0LE_0LA---", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0"),
    ("multi_q3", "1RB1LC_0LA0RF_1RD0LB_1LB0RE_1LF1LG_1RC0LE_0RC---", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0"),
]
for name, tm, t_str in MULTI_Q:
    T = kl.tmpl(tm, t_str)
    evs = kl.blank(tm, 20000000, maxl=40, T=T)
    print(f"\n--- {name}: {tm} ({t_str}) ---")
    for e in evs[:25]:
        if e[0] == 'K':
            print(f"  step {e[1]:9d}: K({short(e[2])}; {e[3]}; {e[4]}) len={len(e[2])}")
        else:
            print(f"  {e}")
