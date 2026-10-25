import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from analyze_1RB1LA_slots import VARIANTS, parse_tm, make_tape_F, is_F_config

HERE = os.path.dirname(os.path.abspath(__file__))

def collect_contexts(tm_str, W, b, max_steps=100000):
    T = parse_tm(tm_str)
    tape, head, q = make_tape_F(W, b)
    ctxs = set()
    for step in range(1, max_steps + 1):
        c = tape.get(head, 0)
        win = tuple(tape.get(head + dc, 0) for dc in range(-4, 5))
        ctxs.add((q, c, win))
        tr = T.get((q, c))
        if tr is None: break
        w, d, nx = tr
        if w == 1: tape[head] = 1
        else: tape.pop(head, None)
        head += d; q = nx
        if is_F_config(tape, head, q) is not None:
            break
    return ctxs

def collect_blank_init(tm_str):
    T = parse_tm(tm_str)
    tape, head, q = {}, 0, 'A'
    ctxs = set()
    for st in range(1, 1000):
        c = tape.get(head, 0)
        win = tuple(tape.get(head + dc, 0) for dc in range(-4, 5))
        ctxs.add((q, c, win))
        w, d, nx = T[(q, c)]
        if w: tape[head] = 1
        else: tape.pop(head, None)
        head += d; q = nx
        if is_F_config(tape, head, q) == ([2, 2], 0):
            break
    return ctxs

tm = VARIANTS[0]
c_init = collect_blank_init(tm)
c_r1_2d = collect_contexts(tm, [2, 2], 0) | collect_contexts(tm, [1, 2], 1) | collect_contexts(tm, [2, 2], 2)
c_r1_1d = collect_contexts(tm, [2], 0) | collect_contexts(tm, [1], 1) | collect_contexts(tm, [3], 2)
c_r3a = collect_contexts(tm, [0, 2], 2) | collect_contexts(tm, [0, 0, 2], 3) | collect_contexts(tm, [0, 1], 6)
c_r4 = collect_contexts(tm, [0], 2) | collect_contexts(tm, [0], 3) | collect_contexts(tm, [0], 14)

non_r4 = c_init | c_r1_2d | c_r1_1d | c_r3a
print("=== Context comparison (including blank->init and 1-digit R1 [d], b) ===")
for radius in (1, 2, 3, 4):
    s_non4 = {(q, c, win[4-radius:4+radius+1]) for (q, c, win) in non_r4}
    s_4 = {(q, c, win[4-radius:4+radius+1]) for (q, c, win) in c_r4}
    diff = s_4 - s_non4
    print(f"Radius {radius} ({2*radius+1}-cell window) in R4 but NOT in (init + R1 + R3A): {len(diff)}")
    for item in sorted(diff):
        print("  ", item)

print("\n=== Analyzing henum_1RB1LA_9.tsv ===")
tsv_path = os.path.join(HERE, 'henum_1RB1LA_9.tsv')
with open(tsv_path, 'r', encoding='utf-8') as f:
    lines = [l.rstrip('\r\n') for l in f if l.strip() and not l.startswith('#')]

print(f"Total interesting lines read: {len(lines)}")

blank_halts = []
intact_r1_r3a = []
partial_r4_halts = []
r4_round2_halts = []
big_maxW = []

for l in lines:
    parts = l.split('\t')
    tag, m, b_info, r1_info, r3a_info = parts[0], parts[1], parts[2], parts[3], parts[4]
    r4_infos = parts[5:11]
    r4_r2 = parts[11] if len(parts) > 11 else ""

    if b_info.startswith('blank=H:'):
        blank_halts.append(parts)
    if r1_info == 'R1=K:()[1,2];1' and r3a_info == 'R3A=K:()[6,1];0':
        intact_r1_r3a.append(parts)
    r4_kinds = [x.split('=')[1][0] for x in r4_infos]
    if 'H' in r4_kinds and 'K' in r4_kinds:
        partial_r4_halts.append(parts)
    if '=H:' in r4_r2:
        r4_round2_halts.append(parts)
    # Check maxW
    for tok in b_info.split(':'):
        if tok.startswith('maxW='):
            mw = int(tok.split('=')[1])
            if mw >= 20:
                big_maxW.append((mw, parts))

print(f"  Blank halts at >= 11,000 steps: {len(blank_halts)}")
for p in blank_halts[:20]:
    print("    " + "\t".join(p[:6]))

print(f"  Intact R1=([1,2];1) and R3A=([6,1];0): {len(intact_r1_r3a)}")
for p in intact_r1_r3a[:25]:
    print("    " + "\t".join(p[:8]))

print(f"  Mixed R4(b) (some H, some K): {len(partial_r4_halts)}")
for p in partial_r4_halts[:20]:
    print("    " + "\t".join(p[:11]))

print(f"  Round-2 R4 halts: {len(r4_round2_halts)}")
for p in r4_round2_halts[:20]:
    print("    " + "\t".join(p))

print(f"  maxW >= 20 in blank run: {len(big_maxW)}")
for mw, p in sorted(big_maxW, reverse=True)[:15]:
    print(f"    maxW={mw}: " + "\t".join(p[:7]))
