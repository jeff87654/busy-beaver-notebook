import collections, json, re, sys

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

def run_from_k(M, t, ds, a, b, maxs=100000, req_B0=None):
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
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    return ('K', k, st)
        if (q, c) not in tr:
            return ('H', chr(65+q) + str(c), st)
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, maxs)

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

cls53_rows = load_tsv('scan_mut8_cls53.tsv')
cand_rows = load_tsv('scan_mut8_cand162.tsv')
all_rows = [('cls53', r) for r in cls53_rows] + [('cand162', r) for r in cand_rows]

# Let's inspect all unique (cat, tm) in B_HITS_HPAR, B_DEP_A_PAR!, NON_MOD2_E!
seen = set()
verdict_counts = collections.Counter()
detailed_results = []

for src, r in all_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!', 'NON_MOD2_E!'):
        continue
    seen.add(tm)
    p = parents[pid]
    t = kl.tmpl(tm, p['tmpl_str'])
    B0 = p['B0']

    # Check B1, B2, B3, B4 at a=5, 6
    b_map = {}
    non_term = False
    for k in range(1, 5):
        r5 = run_from_k(tm, t, [2] + [0]*k, 5, B0, req_B0=B0)
        r6 = run_from_k(tm, t, [2] + [0]*k, 6, B0, req_B0=B0)
        b_map[k] = (r5, r6)

    # Check E(a) for a=6..11 (including actual ds list!)
    e_map = {}
    for a in range(6, 12):
        e_map[a] = run_from_k(tm, t, [], a, B0, req_B0=B0)

    detailed_results.append((src, r, b_map, e_map))

print(f"Evaluated {len(detailed_results)} unique machines in B_HITS_HPAR / B_DEP_A_PAR! / NON_MOD2_E!")

# Group by structural behavior of B1..B4 and E
by_struct = collections.defaultdict(list)
for src, r, b_map, e_map in detailed_results:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    b_sig = []
    for k in range(1, 5):
        r5, r6 = b_map[k]
        if r5[0] == 'K' and r6[0] == 'K':
            ds5, a5, _ = r5[1]
            ds6, a6, _ = r6[1]
            # ds5[0] should be 1 (from 2->1)
            b_sig.append(f"B{k}:{ds5[1:]}({a5%2})/{ds6[1:]}({a6%2})[a={a5}/{a6}]")
        else:
            b_sig.append(f"B{k}:{r5[0]}/{r6[0]}")
    e_sig = []
    for a in (6, 7, 8, 9):
        ra = e_map[a]
        if ra[0] == 'K':
            dsa, aa, _ = ra[1]
            # summarize dsa as run-length
            c = collections.Counter(dsa)
            e_sig.append(f"E{a}:K(len={len(dsa)},vals={dict(c)},end={dsa[-2:] if len(dsa)>=2 else dsa},a={aa})")
        else:
            e_sig.append(f"E{a}:{ra[0]}")
    sig_str = " | ".join(b_sig) + " || " + " ".join(e_sig)
    by_struct[(cat, epat, sig_str)].append((src, r))

print(f"Distinct structural classes: {len(by_struct)}")
for (cat, epat, sig_str), items in sorted(by_struct.items()):
    r0 = items[0][1]
    # Find item with largest maxL or nE
    best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[1][6]).group(1)), int(re.search(r'maxL=(\d+)', x[1][6]).group(1))))[1]
    print(f"\n[{cat}] ({epat}) count={len(items)} | best: {best[0]} {best[2]} {best[6]} {best[7]} | {best[3]}")
    print(f"  {sig_str}")
