"""SAT synthesis of Turing machines from family-rule examples (bounded execution, CaDiCaL via python-sat).

Each example: start word (head just right of it, in state Q, reading blank, all else blank) -> either reach a target
word (same layout) within T steps, or halt within T steps. Unknowns: the 16 transitions (write, move, next state,
or undefined). A0 = 1RB is fixed (TNF). The machine must not halt in a non-halting example.

  python sat_dl.py SPEC.json        -> prints the machine (or UNSAT) and the solve time

SPEC: {"states": 8, "tmpl": {"P": "11", "u": "10", "s": "1", "al": 3, "be": 1, "alB": 3, "beB": 2, "S": "111001", "Q": "B"},
       "fix": {"B0": "1LC"}, "forbid_defined": ["H1"],
       "examples": [{"from": [[2], 2, 1], "to": [[2], 1, 4], "T": 500}, {"from": [[], 0, 1], "halt": true, "T": 350}],
       "margin_left": 4, "margin_right": 6}
"""
import json, sys, time, itertools
from pysat.solvers import Solver

class V:
    def __init__(s): s.n = 0
    def new(s, k=1):
        s.n += k; return list(range(s.n - k + 1, s.n + 1)) if k > 1 else s.n

def word(t, ds, a, b):
    w = t['P']
    for d in ds: w += t['u'] * (t['al'] * d + t['be']) + t['s']
    w += t['u'] * (t['al'] * a + t['be']) + t['s']
    w += t['u'] * (t['alB'] * b + t['beB']) + t['S']
    return w

def build(spec):
    NS = spec['states']; t = spec['tmpl']; Q0 = ord(t['Q']) - 65
    v = V(); cl = []
    # transition variables
    W = {}; D = {}; N = {}; U = {}
    for q in range(NS):
        for c in (0, 1):
            W[q, c] = v.new(); D[q, c] = v.new(); U[q, c] = v.new(); N[q, c] = v.new(NS)
            # exactly one next state unless undefined
            cl.append([U[q, c]] + N[q, c])
            for i, j in itertools.combinations(N[q, c], 2): cl.append([-i, -j])
    def fixtr(name, s):
        q, c = ord(name[0]) - 65, int(name[1])
        cl.append([-U[q, c]]); cl.append([W[q, c] if s[0] == '1' else -W[q, c]])
        cl.append([D[q, c] if s[1] == 'R' else -D[q, c]]); cl.append([N[q, c][ord(s[2]) - 65]])
    fixtr('A0', '1RB')
    for k, s in spec.get('fix', {}).items():
        if s == '---': cl.append([U[ord(k[0]) - 65, int(k[1])]])
        else: fixtr(k, s)
    for k in spec.get('forbid_defined', []): cl.append([U[ord(k[0]) - 65, int(k[1])]])
    ml, mr = spec.get('margin_left', 4), spec.get('margin_right', 6)
    for ex in spec['examples']:
        w0 = word(t, *ex['from']); T = ex['T']
        wt = word(t, *ex['to']) if 'to' in ex else None
        L = max(len(w0), len(wt) if wt else 0) + ml; Wd = L + mr; p0 = L   # cells 0..Wd-1, head starts at p0
        C = [v.new(Wd) for _ in range(T + 1)]; H = [v.new(Wd) for _ in range(T + 1)]
        S = [v.new(NS) for _ in range(T + 1)]; R = [v.new() for _ in range(T + 1)]
        Wt = [v.new() for _ in range(T)]; Dt = [v.new() for _ in range(T)]
        # initial configuration
        for p in range(Wd):
            bit = w0[p - (p0 - len(w0))] == '1' if p0 - len(w0) <= p < p0 else False
            cl.append([C[0][p] if bit else -C[0][p]])
            cl.append([H[0][p] if p == p0 else -H[0][p]])
        for q in range(NS): cl.append([S[0][q] if q == Q0 else -S[0][q]])
        halt_lits = []
        for k in range(T + 1):
            # read symbol
            for p in range(Wd):
                cl.append([-H[k][p], -C[k][p], R[k]]); cl.append([-H[k][p], C[k][p], -R[k]])
            if k == T: break
            for q in range(NS):
                for c in (0, 1):
                    rl = R[k] if c else -R[k]
                    pre = [-S[k][q], -rl]
                    if ex.get('halt'):
                        y = v.new(); halt_lits.append(y)
                        cl += [[-y, S[k][q]], [-y, rl], [-y, U[q, c]]]
                        g = [U[q, c]]          # transitions below only bind when defined
                    else:
                        cl.append(pre + [-U[q, c]]); g = []
                    cl.append(pre + g + [-W[q, c], Wt[k]]); cl.append(pre + g + [W[q, c], -Wt[k]])
                    cl.append(pre + g + [-D[q, c], Dt[k]]); cl.append(pre + g + [D[q, c], -Dt[k]])
                    for q2 in range(NS):
                        cl.append(pre + g + [-N[q, c][q2], S[k + 1][q2]]); cl.append(pre + g + [N[q, c][q2], -S[k + 1][q2]])
            if ex.get('halt'):
                for i, j in itertools.combinations(S[k + 1], 2): cl.append([-i, -j])
                cl.append(S[k + 1][:])
            for p in range(Wd):
                cl.append([-H[k][p], -Wt[k], C[k + 1][p]]); cl.append([-H[k][p], Wt[k], -C[k + 1][p]])
                cl.append([H[k][p], -C[k][p], C[k + 1][p]]); cl.append([H[k][p], C[k][p], -C[k + 1][p]])
                # move (head may not leave the window)
                if p + 1 < Wd: cl.append([-H[k][p], -Dt[k], H[k + 1][p + 1]])
                else: cl.append([-H[k][p], -Dt[k]])
                if p - 1 >= 0: cl.append([-H[k][p], Dt[k], H[k + 1][p - 1]])
                else: cl.append([-H[k][p], Dt[k]])
                # no spurious head
                nb = [H[k][p - 1]] if p - 1 >= 0 else []
                nb += [H[k][p + 1]] if p + 1 < Wd else []
                cl.append([-H[k + 1][p]] + nb)
                if p - 1 >= 0: cl.append([-H[k + 1][p], -H[k][p - 1], Dt[k]])
                if p + 1 < Wd: cl.append([-H[k + 1][p], -H[k][p + 1], -Dt[k]])
        if ex.get('halt'):
            cl.append(halt_lits)
        else:
            # reach the target at some time k
            reach = []
            for k in range(1, T + 1):
                r = v.new(); reach.append(r)
                cl.append([-r, S[k][Q0]]); cl.append([-r, H[k][p0]])
                for p in range(Wd):
                    bit = wt[p - (p0 - len(wt))] == '1' if p0 - len(wt) <= p < p0 else False
                    cl.append([-r, C[k][p] if bit else -C[k][p]])
            cl.append(reach)
    return v, cl, (W, D, N, U)

def decode(model, NS, tr):
    W, D, N, U = tr; m = set(x for x in model if x > 0); rows = []
    for q in range(NS):
        r = ''
        for c in (0, 1):
            if U[q, c] in m: r += '---'
            else: r += ('1' if W[q, c] in m else '0') + ('R' if D[q, c] in m else 'L') + chr(65 + [i for i, x in enumerate(N[q, c]) if x in m][0])
        rows.append(r)
    return '_'.join(rows)

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); t0 = time.time()
    v, cl, tr = build(spec)
    print(f"vars {v.n} clauses {len(cl)} built in {time.time() - t0:.1f}s", flush=True)
    with Solver(name='cadical153', bootstrap_with=cl) as s:
        t1 = time.time(); ok = s.solve()
        print('SAT' if ok else 'UNSAT', f"in {time.time() - t1:.1f}s")
        if ok: print(decode(s.get_model(), spec['states'], tr))
