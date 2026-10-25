import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle

def parse_tm(s):
    parts = s.split('_')
    tm = {}
    for q, p in enumerate(parts):
        for c in (0, 1):
            tr = p[3*c:3*c+3]
            if tr == '---':
                tm[(q, c)] = None
            else:
                tm[(q, c)] = (int(tr[0]), 1 if tr[1] == 'R' else -1, ord(tr[2]) - ord('A'))
    return tm

def mirror_tm(tm):
    return {k: (None if v is None else (v[0], -v[1], v[2])) for k, v in tm.items()}

def run_word(tm, q0, word, steps=2000):
    tape = {}
    for i, ch in enumerate(word):
        tape[i - len(word)] = int(ch)
    p = 0
    q = q0
    used = []
    seen_set = set()
    for st in range(steps):
        c = tape.get(p, 0)
        slot = f"{chr(ord('A')+q)}{c}"
        if slot not in seen_set:
            seen_set.add(slot)
            used.append((st, slot))
        tr = tm[(q, c)]
        if tr is None:
            return 'HALT', st, used
        w, d, nx = tr
        tape[p] = w
        p += d
        q = nx
    return 'END', steps, used

# 1. r4_2_rrFFr: R, B, P=-, u=1, s=10, d=1d+0, b=3b+1, S=-
# word(ds, a, b): each d in ds is 1^d 10, a is 1^a 10, b is 1^(3b+1)
m_r4 = parse_tm("1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE")
print("=== r4_2_rrFFr micro-trace on B2: K([1, 2, 0, 0]; 0; 2) ===")
# ds=[1, 2, 0, 0], a=0, b=2 -> 1 10 11 10 10 10 10 1^7
w_b2 = "1" + "10" + "11" + "10" + "10" + "10" + "10" + "1"*7
tape = {i - len(w_b2): int(ch) for i, ch in enumerate(w_b2)}
p, q = 0, 1 # state B
for st in range(120):
    c = tape.get(p, 0)
    mn, mx = min(tape.keys()), max(tape.keys())
    s_tape = ""
    for i in range(mn, max(mx, p)+1):
        if i == p: s_tape += f"[{chr(ord('A')+q)}]"
        s_tape += str(tape.get(i, 0))
    if st < 60 or (q == 1 and c == 0 and p > mx):
        print(f"  st={st:3d} {chr(ord('A')+q)}{c}: {s_tape}")
    tr = m_r4[(q, c)]
    if tr is None: break
    tape[p] = tr[0]; p += tr[1]; q = tr[2]
