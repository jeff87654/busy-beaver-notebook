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
    s = "0".join("1" * p for p in reversed(parts))
    tape = {i: 1 for i, ch in enumerate(s) if ch == '1'}
    return tape, -1, 0

def is_b5_config(tape, pos, q):
    if q != 0 or tape.get(pos, 0) != 0 or not tape:
        return None
    mn = min(tape.keys())
    mx = max(tape.keys())
    if pos != mn - 1:
        return None
    s = "".join(str(tape.get(i, 0)) for i in range(mn, mx + 1))
    if "00" in s:
        return None
    return list(reversed([len(p) for p in s.split('0')]))

def run_b5_step(tm, parts, max_steps=500000):
    tr = parse_tm(tm)
    tape, pos, q = make_b5_config(parts)
    ctxs, trans_ev = set(), set()
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
        pos += d; q = nq; prev_slot = slot
        res = is_b5_config(tape, pos, q)
        if res is not None:
            return ("K", step, res), ctxs, trans_ev
    return ("TIMEOUT", max_steps, None), ctxs, trans_ev

print("=== 1. Corrected Base-5 12-Digit Rebuilders (reb_base5_1 and reb_base5_2) ===")
for name, tm in [
    ("reb_base5_1", "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"),
    ("reb_base5_2", "1RB1LA_1RC1RE_1RD1RC_0LA0LG_1LD0RF_---0RC_1LE1LG"),
]:
    print(f"\n--- {name}: {tm} ---")
    for p in [
        [3, 3, 5],       # D: d=2 -> 1
        [3, 2, 5],       # D: d=1 -> 0
        [3, 1, 7],       # B1: [..., y+1, 0, b] -> [..., y, b-3, 25]
        [3, 1, 1, 9],    # B2: [..., y+1, 0, 0, b] -> [..., y, b-5, 3, 20]
        [3, 1, 1, 1, 11],# B3: [..., y+1, 0, 0, 0, b] -> [..., y, b-7, 3, 2, 20]
        [2, 1, 7],       # B1 from outer d=1 -> d=0 ([1, 4, 25])
        [1, 1, 9],       # B from outer d=0 ([1, 1, 9] -> ?)
        [1, 9],          # B1 from outer d=0 ([1, 9] -> ?)
        [9], [11], [13]  # E on [B]
    ]:
        ev, _, _ = run_b5_step(tm, p)
        print(f"  {str(p):20s} -> {ev}")

    # Collect init (steps 1..800) + D + B_k + outer-1 contraction vs E ([9], [11], [13], [15])
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
    for p in [
        [3, 3, 5], [3, 2, 5], [3, 2, 25], [2, 2, 5],
        [3, 1, 7], [3, 1, 25], [2, 1, 7], [2, 1, 25],
        [3, 1, 1, 9], [3, 1, 1, 25], [3, 1, 1, 1, 11], [2, 1, 1, 9],
        [1, 2, 5], [1, 1, 9], [1, 9], [1, 25]
    ]:
        _, ctx, tev = run_b5_step(tm, p)
        c_db |= ctx; t_db |= tev

    c_e_common, t_e_common = None, None
    for p in [[9], [11], [13], [15], [25]]:
        _, ctx, tev = run_b5_step(tm, p)
        c_e_common = set(ctx) if c_e_common is None else (c_e_common & ctx)
        t_e_common = set(tev) if t_e_common is None else (t_e_common & tev)

    for r in [0, 1, 2, 3, 4]:
        s_init = {(sl, w[4-r:4+r+1]) for (sl, w) in c_init}
        s_db = {(sl, w[4-r:4+r+1]) for (sl, w) in c_db}
        s_e = {(sl, w[4-r:4+r+1]) for (sl, w) in c_e_common}
        print(f"  r={r}: E_common \\ D/B = {len(s_e - s_db)} | E_common \\ (init+D/B) = {len(s_e - (s_init | s_db))}")
        if r <= 2 and (s_e - s_db):
            for sl, w in sorted(s_e - s_db):
                print(f"    [E \\ D/B] slot={sl} win={''.join(map(str, w))} (in_init={(sl, w) in s_init})")
    print(f"  Transition-resolved 1-step: E_common \\ D/B = { sorted(t_e_common - t_db) } | E_common \\ (init+D/B) = { sorted(t_e_common - (t_init | t_db)) }")
