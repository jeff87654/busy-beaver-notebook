import sys, json
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

def parse_k(w, t):
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
    v = []
    for r in runs[:-1]:
        if r < t['be'] or (r - t['be']) % t['al'] != 0:
            return None
        v.append((r - t['be']) // t['al'])
    return (v[:-1], v[-1], b_val)

def run_k(M, t, ds, a, b, maxs=30000):
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
                k = parse_k(ww, t)
                if k is not None:
                    return ('K', k, st)
        if (q, c) not in tr:
            return ('H', chr(65+q) + str(c), st)
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ('T', None, maxs)

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\parents_profile.json') as f:
    parents = {p['id']: p for p in json.load(f)}

for pid in ['pool8_02', 'pool8_06', 'pool8_07', 'pool8_12', 'pool8_13']:
    p = parents[pid]
    ts = p['tmpl_str'].replace('b=2b+1', 'b=1b+0').replace('b=2b+0', 'b=1b+0')
    t = kl.tmpl(p['machine'], ts)
    outs = []
    for L in range(10, 18):
        knd, r, st = run_k(p['machine'], t, [0]*p['nE'], 0, L, 20000)
        outs.append(f"{L}:K({len(r[0])},a={r[1]},b={r[2]})" if knd == 'K' else f"{L}:{knd}({r})")
    print(pid, ts, ' '.join(outs))
