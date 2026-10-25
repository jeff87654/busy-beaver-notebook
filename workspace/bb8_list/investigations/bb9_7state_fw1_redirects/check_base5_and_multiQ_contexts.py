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

def make_b5_config(parts):
    # parts = [p_k, ..., p_1, b] where A0 is at left end of reversed word:
    # On real tape (left to right): [A0] 1^b 0 1^(p_1) 0 ... 0 1^(p_k)
    s = "0".join("1" * p for p in reversed(parts))
    tape = {i: 1 for i, ch in enumerate(s) if ch == '1'}
    return tape, -1, 0 # pos = -1 (reading 0 to the left of 1^b), q = 0 (state A)

def is_b5_config(tape, pos, q):
    if q != 0 or tape.get(pos, 0) != 0:
        return None
    if not tape:
        return None
    mn = min(tape.keys())
    mx = max(tape.keys())
    if pos != mn - 1:
        return None
    s = "".join(str(tape.get(i, 0)) for i in range(mn, mx + 1))
    if "00" in s:
        return None
    parts = [len(p) for p in s.split('0')]
    return list(reversed(parts))

def run_b5_step(tm, parts, max_steps=500000):
    tr = parse_tm(tm)
    tape, pos, q = make_b5_config(parts)
    ctxs = set()
    trans_ev = set()
    prev_slot = "START"
    for step in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        ctxs.add((slot, win))
        trans_ev.add((prev_slot, slot, tape.get(pos - 1, 0), tape.get(pos + 1, 0)))
        if (q, c) not in tr:
            return ("HALT", step, slot), ctxs, trans_ev
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq
        prev_slot = slot
        res = is_b5_config(tape, pos, q)
        if res is not None:
            return ("K", step, res), ctxs, trans_ev
    return ("TIMEOUT", max_steps, None), ctxs, trans_ev

print("=== 1. Testing Base-5 12-Digit Rebuilders (reb_base5_1 and reb_base5_2) ===")
for name, tm in [
    ("reb_base5_1", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"),
    ("reb_base5_2", "1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"),
]:
    print(f"\n--- {name}: {tm} ---")
    for p in [
        [3, 3, 5], [3, 2, 7], [3, 2, 2, 9], [3, 2, 2, 2, 11],
        [2, 3, 5], [2, 2, 9], [2, 9], [2, 11], [9], [11], [8], [10]
    ]:
        ev, _, _ = run_b5_step(tm, p)
        print(f"  {str(p):22s} -> {ev}")

    # Collect init (steps 1..800) + D + B_k vs E ([2^k, B] and [B] for odd B=9,11,13,15)
    tr = parse_tm(tm)
    tape, pos, q = {}, 0, 0
    c_init, t_init = set(), set()
    prev_slot = "START"
    for st in range(1, 801):
        c = tape.get(pos, 0)
        slot = chr(65 + q) + str(c)
        win = tuple(tape.get(pos + dc, 0) for dc in range(-4, 5))
        c_init.add((slot, win))
        t_init.add((prev_slot, slot, tape.get(pos - 1, 0), tape.get(pos + 1, 0)))
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d; q = nq; prev_slot = slot

    c_db, t_db = set(), set()
    for p in [[3, 4, 5], [3, 3, 5], [3, 4, 25], [3, 3, 2, 7], [3, 3, 2, 2, 11], [3, 2, 2, 2, 13], [4, 2, 9]]:
        _, ctx, tev = run_b5_step(tm, p)
        c_db |= ctx; t_db |= tev

    c_e_common, t_e_common = None, None
    for p in [[9], [11], [13], [2, 9], [2, 2, 11]]:
        _, ctx, tev = run_b5_step(tm, p)
        c_e_common = set(ctx) if c_e_common is None else (c_e_common & ctx)
        t_e_common = set(tev) if t_e_common is None else (t_e_common & tev)

    for r in [0, 1, 2, 3, 4]:
        s_base = {(sl, w[4-r:4+r+1]) for (sl, w) in (c_init | c_db)}
        s_e = {(sl, w[4-r:4+r+1]) for (sl, w) in c_e_common}
        s_db = {(sl, w[4-r:4+r+1]) for (sl, w) in c_db}
        print(f"  r={r}: E_common \\ D/B = {len(s_e - s_db)} | E_common \\ (init+D/B) = {len(s_e - s_base)}")
    print(f"  Transition-resolved 1-step: E_common \\ D/B = { sorted(t_e_common - t_db) } | E_common \\ (init+D/B) = { sorted(t_e_common - (t_init | t_db)) }")

print("\n=== 2. Testing multi_q1, multi_q2, multi_q3 macro rules ===")
MULTI_Q = [
    ("multi_q1", "1RB1LC_0LA---_1RD0LG_1LG0RE_1LF0LB_1RC0LE_0LA0RF", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0"),
    ("multi_q2", "1RB1LC_0LA0RF_1RD0LB_1LB0RE_1LF0LG_1RC0LE_0LA---", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0"),
    ("multi_q3", "1RB1LC_0LA0RF_1RD0LB_1LB0RE_1LF1LG_1RC0LE_0RC---", "R,E,P=110,u=011,s=0,d=1d+0,b=2b+0,S=0"),
]
for name, tm, t_str in MULTI_Q:
    T = kl.tmpl(tm, t_str)
    print(f"\n--- {name}: {tm} ---")
    for ds in [[1, 2], [1, 1, 0], [1, 1, 0, 0], [1, 0], [0, 0], [0], []]:
        for a in [1, 4]:
            evs = kl.run(tm, ds, a, 1, steps=300000, nchg=0, maxl=30, T=T, pall=1)
            b1 = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K' and e[4] == 1][:3]
            h = [f"H({e[2]}{e[3]})@{e[1]}" for e in evs[1:] if e[0] == 'H']
            print(f"  K({short(ds):6s}; a={a}; 1) -> {b1 + h}")
