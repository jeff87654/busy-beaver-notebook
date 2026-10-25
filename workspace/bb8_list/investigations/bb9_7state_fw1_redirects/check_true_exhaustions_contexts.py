import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def parse_tm(tm, mir=False):
    tr = {}
    for q, row in enumerate(tm.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    return tr

def trace_blank_ctxs(tm, max_steps):
    tr = parse_tm(tm, mir=False)
    tape = {}
    pos = 0
    q = 0
    ctxs = set()
    for step in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        if (q, c) not in tr:
            break
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
    return ctxs

def trace_k_ctxs(tm, t_str, B0, ds, a, maxs=300000):
    t = kl.tmpl(tm, t_str)
    evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=100, T=t, pall=1)
    ev1 = ('END',)
    stop_step = maxs
    for e in evs[1:]:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == B0 and e[2] != ds):
            ev1 = e
            stop_step = e[1]
            break
    mir = (t['o'] == 'L')
    tr = parse_tm(tm, mir=False)
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
    ctxs = set()
    for step in range(1, stop_step + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        if (q, c) not in tr:
            break
        W_bit, d, nq = tr[(q, c)]
        if W_bit: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
    return ev1, ctxs

# 1. reb_E2: Compare E_1 = K(1, 0^k; a; 1) and E_2 = K(1, 0^k, 1; a; 1) against init(1..415) + all D/B_k
tm_E2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_E2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"

c_init_E2 = trace_blank_ctxs(tm_E2, 415)
c_db_r1_E2 = set() # D and B_k occurring in Round 1 (all inner digits even, outer digit 5 or 3)
for ds in [[5, 4], [5, 2], [3, 4], [5, 4, 0], [5, 4, 0, 0], [5, 4, 0, 0, 0], [5, 0, 0], [3, 0, 0], [3, 0, 0, 0]]:
    for a in [3, 5, 9]:
        _, ctx = trace_k_ctxs(tm_E2, t_E2, 1, ds, a)
        c_db_r1_E2 |= ctx

c_db_r2_E2 = set(c_db_r1_E2) # Plus inner odd digit borrows occurring in Round 2
for ds in [[5, 3], [5, 2, 1], [5, 2, 1, 0], [5, 2, 1, 0, 0], [5, 0, 1, 0], [3, 1], [3, 0, 1], [3, 0, 0, 1], [1, 3], [1, 0, 3]]:
    for a in [3, 5, 7]:
        _, ctx = trace_k_ctxs(tm_E2, t_E2, 1, ds, a)
        c_db_r2_E2 |= ctx

c_e1_common = None
for k in [2, 3, 5]:
    for a in [7, 9]:
        ev, ctx = trace_k_ctxs(tm_E2, t_E2, 1, [1] + [0]*k, a)
        c_e1_common = set(ctx) if c_e1_common is None else (c_e1_common & ctx)

c_e2_common = None
for k in [2, 3]:
    for a in [7, 9]:
        ev, ctx = trace_k_ctxs(tm_E2, t_E2, 1, [1] + [0]*k + [1], a)
        c_e2_common = set(ctx) if c_e2_common is None else (c_e2_common & ctx)

print("=== reb_E2: E_1 = K(1, 0^k; a; 1) vs (init(1..415) + Round-1 D/B_k) ===")
for r in [0, 1, 2, 3, 4]:
    s_base = {(sl, w[4-r:4+r+1]) for (sl, w) in (c_init_E2 | c_db_r1_E2)}
    s_e1 = {(sl, w[4-r:4+r+1]) for (sl, w) in c_e1_common}
    diff = sorted(s_e1 - s_base)
    print(f"  r={r} ({2*r+1}-cell): E1_common \\ (init + R1_DB) = {len(diff)}")
    for sl, w in diff[:10]:
        print(f"    slot={sl} win={''.join(map(str, w))}")

print("\n=== reb_E2: E_2 = K(1, 0^k, 1; a; 1) vs (init + R1_DB + E1 + R2_DB) ===")
for r in [0, 1, 2, 3, 4]:
    s_base = {(sl, w[4-r:4+r+1]) for (sl, w) in (c_init_E2 | c_db_r2_E2 | c_e1_common)}
    s_e2 = {(sl, w[4-r:4+r+1]) for (sl, w) in c_e2_common}
    diff = sorted(s_e2 - s_base)
    print(f"  r={r} ({2*r+1}-cell): E2_common \\ (init + R1_DB + E1 + R2_DB) = {len(diff)}")
    for sl, w in diff[:10]:
        print(f"    slot={sl} win={''.join(map(str, w))}")

# 2. Check multi_1 and w1loop_1 full cycle from a small synthetic config!
print("\n=== multi_1: Full trajectory from K(1; 1; 1) and K(2, 0; 1; 1) ===")
tm_m1 = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
t_m1 = "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1"
T_m1 = kl.tmpl(tm_m1, t_m1)
for ds in [[1], [2, 0]]:
    evs = kl.run(tm_m1, ds, 1, 1, steps=500000, nchg=0, maxl=60, T=T_m1, pall=1)
    b1_evs = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs if e[0] == 'K' and e[4] == 1]
    print(f"  multi_1 from K({short(ds)}; 1; 1): {b1_evs[:12]}")

print("\n=== w1loop_1: Full trajectory from K(1; 1; 1) ===")
tm_w1 = "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---"
t_w1 = "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-"
T_w1 = kl.tmpl(tm_w1, t_w1)
evs = kl.run(tm_w1, [1], 1, 1, steps=500000, nchg=0, maxl=60, T=T_w1, pall=1)
b1_evs = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs if e[0] == 'K' and e[4] == 1]
print(f"  w1loop_1 from K(1; 1; 1): {b1_evs[:12]}")
