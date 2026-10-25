import os, sys, json, re, ctypes
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl

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

def run_from_k(M, t, ds, a, b, maxs=200000, req_B0=None):
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
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    return ('K', k, used, st)
        if (q, c) not in tr:
            return ('H', (chr(65+q) + str(c)), used, st)
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, used, maxs)

def run_blank_to_big_k(M, t, min_len=5, maxs=50000, req_B0=None):
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
    used = set()
    first_k_used = None
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    if first_k_used is None:
                        first_k_used = (st, k, set(used))
                    if len(k[0]) >= min_len:
                        return ('BIG_K', (st, k), used, first_k_used)
        if (q, c) not in tr:
            return ('H', st, used, first_k_used)
        used.add(chr(65+q) + str(c))
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('END', maxs, used, first_k_used)

# Load parents
parents = []
verdicts_path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\noinv53_verdicts.tsv'
with open(verdicts_path) as f:
    hdr = f.readline()
    for line in f:
        parts = line.rstrip('\n').split('\t')
        idx = int(parts[0])
        tag = parts[1]
        fam = parts[2]
        m = parts[3]
        btrace = parts[4]
        grp = parts[5]
        verd = parts[6]
        rnds = parts[7]
        gcls = parts[8]
        if 'FOMEGA' in gcls or 'TETRATIONAL' in gcls:
            _, tmpl_str, B0, _ = bcfg.BASES[tag]
            parents.append({
                'id': f'cls53_{idx:02d}_{tag}',
                'source': 'cls53',
                'tag': tag,
                'group': grp,
                'machine': m,
                'tmpl_str': tmpl_str,
                'B0': B0,
                'verdict': verd,
                'btrace': btrace,
                'mode': 'b_acc' if (grp in ('B_HALT_E2', 'ACK_RESID')) else 'a_acc',
                'nE': 0
            })

run8_path = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\run8.jsonl'
with open(run8_path) as f:
    for i, line in enumerate(f, 1):
        d = json.loads(line)
        if i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 21, 23):
            m = d['machine']
            tmpl_str = d.get('tmpl') or d.get('tmpl_in')
            used_n = d.get('E_used_n', [])
            nE = int(used_n[0]) if (used_n and str(used_n[0]).isdigit()) else 0
            parents.append({
                'id': f'pool8_{i:02d}',
                'source': 'pool8',
                'tag': f'p8_{i:02d}',
                'group': f'POOL8_{i:02d}',
                'machine': m,
                'tmpl_str': tmpl_str,
                'B0': 0,
                'verdict': d.get('verdict', ''),
                'btrace': str(d.get('first_K', '')),
                'mode': 'b_acc',
                'nE': nE
            })

# Also add representative intact KHKH leaves from cand162_blank.tsv
cand_path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\cand162_blank.tsv'
seen_grp = set()
with open(cand_path) as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        tag, slot_tag, mx, cyc, m, st, nK, nE_cnt, max_len = parts[:9]
        ev = parts[9] if len(parts) > 9 else ''
        key = (tag, slot_tag, mx, cyc, ev.strip()[:15])
        if key not in seen_grp and (int(max_len) >= 10 or cyc == 'True' or int(mx) >= 1):
            seen_grp.add(key)
            _, tmpl_str, B0, _ = bcfg.BASES[tag]
            parents.append({
                'id': f'cand162_{tag}_{slot_tag}_{len(seen_grp):02d}',
                'source': 'cand162',
                'tag': tag,
                'group': f'CAND_{tag}_{slot_tag}',
                'machine': m,
                'tmpl_str': tmpl_str,
                'B0': B0,
                'verdict': f'maxR={mx},cyc={cyc}',
                'btrace': ev.strip()[:40],
                'mode': 'a_acc',
                'nE': 0
            })

print(f"Total parents collected: {len(parents)}")

# Profile transition roles for each parent
out_rows = []
for p in parents:
    M = p['machine']
    t = kl.tmpl(M, p['tmpl_str'])
    B0 = p['B0']
    nE = p['nE']
    all_def = set()
    undef = []
    for q, row in enumerate(M.split('_')):
        for c in range(2):
            s = chr(65+q) + str(c)
            if row[3*c] == '-':
                undef.append(s)
            else:
                all_def.add(s)

    if p['mode'] == 'a_acc':
        D_cfgs = [([3], 4, B0), ([3], 5, B0)]
        B_cfgs = [([2] + [0]*k, a, B0) for k in (1, 2, 3) for a in (5, 6)]
        E_cfgs = [([0]*nE, a, B0) for a in (6, 7, 8, 9, 10, 11)]
    else:
        D_cfgs = [([3], 2, 10), ([3], 3, 11), ([3], 0, 10), ([3], 0, 11), ([3], 1, 10), ([3], 1, 11)]
        B_cfgs = [([2] + [0]*k, a, b) for k in (1, 2, 3) for a in (0, 1) for b in (10, 11)]
        E_cfgs = [([0]*nE, a, b) for a in (0, 1) for b in (12, 13, 14, 15, 16, 17)]

    req_B0 = B0 if p['mode'] == 'a_acc' else None
    D_used = set()
    for ds, a, b in D_cfgs:
        _, _, u, _ = run_from_k(M, t, ds, a, b, 50000, req_B0=req_B0)
        D_used |= u

    B_used = set()
    for ds, a, b in B_cfgs:
        _, _, u, _ = run_from_k(M, t, ds, a, b, 50000, req_B0=req_B0)
        B_used |= u

    E_used = set()
    E_halt_slots = set()
    for ds, a, b in E_cfgs:
        knd, r, u, _ = run_from_k(M, t, ds, a, b, 50000, req_B0=req_B0)
        E_used |= u
        if knd == 'H':
            E_halt_slots.add(r)

    _, _, blank_used, fk = run_blank_to_big_k(M, t, min_len=5, maxs=50000, req_B0=req_B0)
    fk_used = fk[2] if fk else set()

    B_only = sorted(B_used - D_used)
    E_only = sorted(E_used - D_used - B_used)
    start_only = sorted(blank_used - D_used - B_used - E_used)
    unused_all = sorted(all_def - (D_used | B_used | E_used | blank_used))

    p['undef'] = undef
    p['D_used'] = sorted(D_used)
    p['B_only'] = B_only
    p['E_only'] = E_only
    p['start_only'] = start_only
    p['unused_all'] = unused_all
    out_rows.append(p)

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\parents_profile.json', 'w') as f:
    json.dump(out_rows, f, indent=2)

print("Summary of transition roles across parents:")
for p in out_rows[:65]:
    print(f"{p['id']:18s} | grp={p['group']:14s} | U={','.join(p['undef'])} | B_only={','.join(p['B_only']) or '-':8s} | E_only={','.join(p['E_only']) or '-':8s} | start={','.join(p['start_only']) or '-':6s} | unused={','.join(p['unused_all']) or '-'}")
