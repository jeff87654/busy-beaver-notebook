import json, sys
BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from classify_all_mut8_exact import all_rows, parents, analyze_a_acc_symbolic, kl, run_from_k, parse_k

def get_blank_k_seq(M, t, maxs=50000, req_B0=None):
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
    ks = []
    for st in range(maxs):
        c = tape.get(pos, 0)
        if st > 0 and c == 0 and q == Q:
            ones = [i for i, v in tape.items() if v]
            if ones and pos > max(ones):
                lo = min(ones)
                ww = ''.join(str(tape.get(i, 0)) for i in range(lo, pos))
                k = parse_k(ww, t, req_B0=req_B0)
                if k is not None:
                    ks.append((st, k))
                    if len(ks) >= 6:
                        break
        if (q, c) not in tr:
            break
        W, d, nq = tr[(q, c)]
        tape[pos] = W
        pos += d
        q = nq
    return ks

seen = set()
for src, r in all_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!'):
        continue
    seen.add(tm)
    p = parents[pid]
    res = analyze_a_acc_symbolic(tm, p)
    if isinstance(res, str):
        continue
    b1_len = len(res[1][0][0])
    b1_p0, b1_p1 = res[1][0][1], res[1][1][1]
    b2_len = len(res[2][0][0])
    b2_p0, b2_p1 = res[2][0][1], res[2][1][1]
    if b1_len == 1 and b1_p0 == 1 and b2_len == 1 and b2_p0 == 0:
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        ks = get_blank_k_seq(tm, t, maxs=50000, req_B0=B0)
        print(f"{pid:14s} {mut:16s} | {tm}")
        print(f"  binfo={binfo} | btrace={btrace}")
        for st, k in ks[:4]:
            print(f"    st={st:6d}: ds={k[0]} (len={len(k[0])}), a={k[1]}, b={k[2]}")
