import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def parse_tm(tm):
    tr = {}
    for q, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), d, ord(x[2]) - 65)
    return tr

def is_b5_config(tape, pos, q):
    if q != 0 or tape.get(pos, 0) != 0 or not tape:
        return None
    mn = min(tape.keys())
    mx = max(tape.keys())
    if pos != mn - 1:
        return None
    s = "".join(str(tape.get(i, 0)) for i in range(mn, mx + 1))
    return list(reversed([len(p) for p in s.split('0')]))

print("=== 1. All A0 (b5_config) moments on blank tape of reb_base5_1 up to step 5000 ===")
tm_b5_1 = "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"
tr = parse_tm(tm_b5_1)
tape, pos, q = {}, 0, 0
for st in range(1, 5000):
    res = is_b5_config(tape, pos, q)
    if res is not None:
        print(f"  step {st:5d}: parts={res}")
    c = tape.get(pos, 0)
    w, d, nq = tr[(q, c)]
    if w: tape[pos] = 1
    else: tape.pop(pos, None)
    pos += d; q = nq

print("\n=== 2. Check multi_1, w1loop_1, multi_q1, multi_q2, multi_q3 for E_common \\ (init + D + B_k) ===")
# Note: In multi_1, w1loop_1, multi_q1..3, what happens during init?
# Does init ALREADY execute E(; 1; 1) to build the initial list?!
# Let's check!
# - In multi_1: step 115 is K(; 2; 0) -> step 344 is K(; 4; 1) -> step 1848 is K(2, 0, 1^8; 1; 1)!
#   WAIT: step 344 -> step 1848 IS E(; a=2; 1)!
# - In w1loop_1: step 100 is K(; 1; 1) -> step 392 is K(1^3; 1; 1)!
#   WAIT: step 100 -> step 392 IS E(; a=1; 1)!
# - In multi_q1..3: step 155 is K(; 1; 1) -> step 1832 is K(1^8; 1; 1)!
#   WAIT: step 155 -> step 1832 IS E(; a=1; 1)!
# What about E(; a; 1) for a >= 4 (since after Round 1, A_final >= 4) vs init (where E ran on a=1 or a=2) + D + B_k + boundary contraction K(0^m; a; 1)?!

def trace_k_trans_full(tm, t_str, B0, ds, a, maxs=500000):
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
    tr = parse_tm(tm)
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
    ctxs, tev = set(), set()
    prev_slot = "START"
    for step in range(1, stop_step + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        tev.add((prev_slot, slot, tape.get(pos - 1, 0), tape.get(pos + 1, 0)))
        if (q, c) not in tr:
            break
        W_bit, d, nq = tr[(q, c)]
        if W_bit: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq; prev_slot = slot
    return ev1, ctxs, tev

def trace_blank_full(tm, max_steps):
    tr = parse_tm(tm)
    tape, pos, q = {}, 0, 0
    ctxs, tev = set(), set()
    prev_slot = "START"
    for step in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        tev.add((prev_slot, slot, tape.get(pos - 1, 0), tape.get(pos + 1, 0)))
        if (q, c) not in tr:
            break
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq; prev_slot = slot
    return ctxs, tev

FAMS = [
    ("multi_1", "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF", "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1", 1, 1848,
     [([2,0,1,1], 1), ([2,0,1,0], 4), ([2,0,1,0,0], 4), ([2,0,0], 4), ([1,0], 4), ([0], 1)],
     [([], 4), ([], 10)]),
    ("w1loop_1", "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---", "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-", 1, 392,
     [([1,1], 1), ([1,2], 1), ([1,1,0], 4), ([1,1,0,0], 4), ([1,0], 1)],
     [([0], 1), ([], 4), ([], 10)]),
    ("multi_q1", "1RB1LC_0LA---_1RD0LG_1LG0RE_1LF0LB_1RC0LE_0LA0RF", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0", 1, 1832,
     [([1,1], 1), ([1,2], 1), ([1,1,0], 4), ([1,1,0,0], 4), ([1,0], 4), ([0,0], 1), ([0], 1)],
     [([], 4), ([], 10)]),
    ("multi_q2", "1RB1LC_0LA0RF_1RD0LB_1LB0RE_1LF0LG_1RC0LE_0LA---", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0", 1, 1832,
     [([1,1], 1), ([1,2], 1), ([1,1,0], 4), ([1,1,0,0], 4), ([1,0], 4), ([0,0], 1), ([0], 1)],
     [([], 4), ([], 10)]),
    ("multi_q3", "1RB1LC_0LA0RF_1RD0LB_1LB0RE_1LF1LG_1RC0LE_0RC---", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0", 1, 1870,
     [([1,1], 1), ([1,2], 1), ([1,1,0], 4), ([1,1,0,0], 4), ([1,0], 4), ([0,0], 1), ([0], 1)],
     [([], 4), ([], 10)]),
]

for name, tm, t_str, B0, init_st, db_list, e_list in FAMS:
    c_init, t_init = trace_blank_full(tm, init_st)
    c_db, t_db = set(), set()
    for ds, a in db_list:
        _, ctx, tev = trace_k_trans_full(tm, t_str, B0, ds, a)
        c_db |= ctx; t_db |= tev
    c_ec, t_ec = None, None
    for ds, a in e_list:
        ev, ctx, tev = trace_k_trans_full(tm, t_str, B0, ds, a)
        c_ec = set(ctx) if c_ec is None else (c_ec & ctx)
        t_ec = set(tev) if t_ec is None else (t_ec & tev)
    print(f"\n--- {name}: {tm} ---")
    for r in [0, 1, 2, 3, 4]:
        s_base = {(sl, w[4-r:4+r+1]) for (sl, w) in (c_init | c_db)}
        s_db = {(sl, w[4-r:4+r+1]) for (sl, w) in c_db}
        s_e = {(sl, w[4-r:4+r+1]) for (sl, w) in c_ec}
        print(f"  r={r}: E_common \\ D/B = {len(s_e - s_db)} | E_common \\ (init+D/B) = {len(s_e - s_base)}")
    print(f"  Trans 1-step: E_common \\ D/B = {sorted(t_ec - t_db)} | E_common \\ (init+D/B) = {sorted(t_ec - (t_init | t_db))}")
