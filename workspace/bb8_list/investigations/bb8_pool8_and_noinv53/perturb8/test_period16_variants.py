import os, json, sys, ctypes

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl

parents = {p['id']: p for p in json.load(open(BASE + r'\parents_profile.json'))}

def parse_k(w, t, req_B0=None):
    P, S, u, s = t['P'], t['S'], t['u'], t['s']
    if not (w.startswith(P) and w.endswith(S)) or len(w) < len(P)+len(S):
        return None
    body = w[len(P):len(w)-len(S)]
    runs = []
    i = 0
    e = len(body)
    while True:
        k = 0
        i0 = i
        while i + len(u) <= e and body[i:i+len(u)] == u:
            i += len(u)
            k += 1
        if i == e:
            runs.append(k)
            break
        fs = False
        for kk in range(k, -1, -1):
            j = i0 + kk * len(u)
            if j + len(s) <= e and body[j:j+len(s)] == s:
                runs.append(kk)
                i = j + len(s)
                fs = True
                break
        if not fs:
            return None
    if len(runs) < 2:
        return None
    bl = runs[-1]
    if bl < t['beB'] or (bl - t['beB']) % t['alB'] != 0:
        return None
    b_val = (bl - t['beB']) // t['alB']
    if req_B0 is not None and b_val != req_B0:
        return None
    v = []
    for r in runs[:-1]:
        if r < t['be'] or (r - t['be']) % t['al'] != 0:
            return None
        v.append((r - t['be']) // t['al'])
    return (v[:-1], v[-1], b_val)

def get_used_in_k(M, t, ds, a, b, maxs=20000):
    mir = t['o'] == 'L'
    tr = {}
    for q, row in enumerate(M.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    w = kl.word(t, ds, a, b)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos = len(w)
    Q = ord(t['q']) - 65
    q = Q
    used = set()
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=b)
                if k is not None:
                    return ('K', k, st, sorted(used))
        if (q, c) not in tr:
            return ('H', chr(65+q) + str(c), st, sorted(used))
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, maxs, sorted(used))

def trace_blank(M, t, B0, maxs=200):
    mir = t['o'] == 'L'
    tr = {}
    for q, row in enumerate(M.split('_')):
        for c in range(2):
            x = row[3*c:3*c+3]
            if x[0] != '-':
                d = 1 if x[1] == 'R' else -1
                tr[(q, c)] = (int(x[0]), -d if mir else d, ord(x[2]) - 65)
    tape = {}
    pos = 0
    Q = ord(t['q']) - 65
    q = 0
    used = []
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=B0)
                if k is not None:
                    return ('K', k, st, used)
        if (q, c) not in tr:
            return ('H', chr(65+q)+str(c), st, used)
        used.append(chr(65+q)+str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, maxs, used)

p = parents['cls53_09_f']
tm8 = "1RB1RA_0LC0LF_1RD1LC_1LE1RE_1LB0RG_0LH1LF_1LG0RA_0RD---"
t = kl.tmpl(tm8, p['tmpl_str'])
B0 = p['B0']

res_b = trace_blank(tm8, t, B0, maxs=500)
print("trace_blank(tm8):", res_b[:3], "transitions:", res_b[3])

for name, ds, a in [
    ("D(2)", [2], 2),
    ("B1(2)", [2, 0], 2),
    ("B2(2)", [2, 0, 0], 2),
    ("B3(2)", [2, 0, 0, 0], 2),
    ("E(1)", [], 1),
    ("E(0)", [], 0),
    ("E(4)", [], 4),
]:
    r = get_used_in_k(tm8, t, ds, a, B0)
    print(f"  {name}: {r[0]} ({r[1]}) steps={r[2]} used={r[3]}")
