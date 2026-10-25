import os, json, re, collections, sys, ctypes

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

def get_blank_k_seq(M, t, req_B0=None, maxs=400000):
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
    seq = []
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    seq.append((st, k))
                    if len(seq) >= 8:
                        break
        if (q, c) not in tr:
            seq.append(('H', chr(65+q)+str(c), st))
            break
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return seq

p1 = parents['cls53_38_p']
tm3 = "1RB1LA_1LC1RE_1RD1RC_0LA0LG_1RG0RF_1LF0RC_1LH1LG_1LD0LI_---0LA"
t1 = kl.tmpl(tm3, p1['tmpl_str'])
B0 = p1['B0']

print("=== Blank k_seq of KHTKHTKH (tm3) ===")
for item in get_blank_k_seq(tm3, t1, req_B0=B0):
    print(" ", item)

def parse_bk_det(b_str):
    if '/' in b_str:
        p0, p1 = b_str.split('/', 1)
    else:
        p0, p1 = b_str, b_str
    def parse_one(p):
        m = re.match(r'^\[([^\]]*)\];(-?\d+);(-?\d+)$', p)
        if not m:
            return None
        L = []
        for x in m.group(1).split(','):
            x = x.strip()
            if not x:
                continue
            if '^' in x:
                val, cnt = x.split('^')
                L.extend([int(val)] * int(cnt))
            else:
                L.append(int(x))
        a = int(m.group(2))
        return (L[1:], a % 2, a)
    r0 = parse_one(p0)
    r1 = parse_one(p1)
    if not r0 or not r1:
        return None
    return (r0, r1)

def load_tsv(fn):
    path = BASE + '\\' + fn
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='ignore')
    rows = []
    for line in text.splitlines():
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) >= 9:
            rows.append(parts[:9])
    return rows

extra_rows = load_tsv('scan_ext9_extra.tsv')
seen = set()
by_b_struct = collections.defaultdict(list)
for r in extra_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!', 'NON_MOD2_E!'):
        continue
    seen.add(tm)
    m1 = re.search(r'B1=([^\s]+)', det)
    m2 = re.search(r'B2=([^\s]+)', det)
    m3 = re.search(r'B3=([^\s]+)', det)
    b1 = parse_bk_det(m1.group(1)) if m1 else None
    b2 = parse_bk_det(m2.group(1)) if m2 else None
    b3 = parse_bk_det(m3.group(1)) if m3 else None
    if b1 and b2 and b3:
        l1 = len(b1[0][0])
        if l1 > 1:
            key = f"{epat} | RUNAWAY_B1 (l1={l1})"
        else:
            p1_0, p1_1 = b1[0][1], b1[1][1]
            l2 = len(b2[0][0])
            p2_0, p2_1 = b2[0][1], b2[1][1]
            t2 = b2[0][0][1:]
            l3 = len(b3[0][0])
            p3_0, p3_1 = b3[0][1], b3[1][1]
            t3 = b3[0][0][1:]
            key = f"{epat} | B1(l={l1},p={p1_0}/{p1_1}) B2(l={l2},p={p2_0}/{p2_1},t={t2}) B3(l={l3},p={p3_0}/{p3_1},t={t3})"
    else:
        key = f"{epat} | OTHER ({det[:50]})"
    by_b_struct[key].append(r)

print(f"\n=== {len(seen)} UNIQUE INTERESTING MACHINES IN scan_ext9_extra.tsv ACROSS {len(by_b_struct)} CLASSES ===")
for key, items in sorted(by_b_struct.items()):
    best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[6]).group(1)), int(re.search(r'maxL=(\d+)', x[6]).group(1))))
    print(f"  {len(items):4d}x : {key}")
    print(f"         best: {best[0]} {best[2]} {best[6]} {best[7]} | {best[3]}")
