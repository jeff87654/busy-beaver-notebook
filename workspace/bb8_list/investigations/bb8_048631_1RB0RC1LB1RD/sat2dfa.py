"""SAT search for a two-DFA closed relation certificate (left DFA reads far->near, right DFA reads far->near).
usage: python sat2dfa.py MACHINE nL nR [timeout_s]
Certificate: dL[s][x]->s', dR[s][x]->s', R subset Q x SL x SR.
Config (q, l, r): l = rev(wl)+zeros, r = rev(wr)+zeros (scanned cell = hd r = last char of wr);
 aL = runL(wl), aR = runR(wr). R(q,aL,aR) must hold; closure as in notes."""
import sys, itertools, time, json
from pysat.solvers import Solver

def parse(M):
    T = {}
    for qi, part in enumerate(M.split('_')):
        for s in (0, 1):
            t = part[3*s:3*s+3]
            T[(qi, s)] = None if t == '---' else (int(t[0]), t[1], ord(t[2]) - 65)
    return T

def build(M, nL, nR):
    T = parse(M)
    NQ = len(M.split('_'))
    cnt = [0]
    def new():
        cnt[0] += 1
        return cnt[0]
    cl = []
    dL = [[[new() for _ in range(nL)] for _ in range(2)] for _ in range(nL)]
    dR = [[[new() for _ in range(nR)] for _ in range(2)] for _ in range(nR)]
    for tab, n in ((dL, nL), (dR, nR)):
        for s in range(n):
            for x in range(2):
                cl.append(tab[s][x][:])
                for i, j in itertools.combinations(range(n), 2):
                    cl.append([-tab[s][x][i], -tab[s][x][j]])
    cl.append([dL[0][0][0]]); cl.append([dR[0][0][0]])
    R = [[[new() for _ in range(nR)] for _ in range(nL)] for _ in range(NQ)]
    cl.append([R[0][0][0]])
    # Pop[q][a][c][s'] <- R[q][a][b] & dR[s'][c][b]
    Pop = {}
    for q in range(NQ):
        for c in range(2):
            for a in range(nL):
                for s in range(nR):
                    v = new(); Pop[q, a, c, s] = v
                    for b in range(nR):
                        cl.append([-R[q][a][b], -dR[s][c][b], v])
    # Z[s][w][x][v] <- dR[s][w][u] & dR[u][x][v]
    Z = {}
    for s in range(nR):
        for w in range(2):
            for x in range(2):
                for v in range(nR):
                    z = new(); Z[s, w, x, v] = z
                    for u in range(nR):
                        cl.append([-dR[s][w][u], -dR[u][x][v], z])
    for q in range(NQ):
        for c in range(2):
            tr = T[(q, c)]
            for a in range(nL):
                for s in range(nR):
                    p = Pop[q, a, c, s]
                    if tr is None:
                        cl.append([-p]); continue
                    w, d, q2 = tr
                    if d == 'R':
                        for t in range(nL):
                            cl.append([-p, -dL[a][w][t], R[q2][t][s]])
                    else:
                        for a0 in range(nL):
                            for x in range(2):
                                for v in range(nR):
                                    cl.append([-p, -dL[a0][x][a], -Z[s, w, x, v], R[q2][a0][v]])
    return cl, dL, dR, R, cnt[0]

def solve(M, nL, nR, timeout=None):
    cl, dL, dR, R, nv = build(M, nL, nR)
    t0 = time.time()
    with Solver(name='cadical153', bootstrap_with=cl) as s:
        ok = s.solve()
        dt = time.time() - t0
        if not ok:
            return None, dt
        m = set(x for x in s.get_model() if x > 0)
        resL = [[next(t for t in range(nL) if dL[s_][x][t] in m) for x in range(2)] for s_ in range(nL)]
        resR = [[next(t for t in range(nR) if dR[s_][x][t] in m) for x in range(2)] for s_ in range(nR)]
        Rs = [(q, a, b) for q in range(len(R)) for a in range(nL) for b in range(nR) if R[q][a][b] in m]
        return {'dL': resL, 'dR': resR, 'R': Rs}, dt

if __name__ == '__main__':
    M = sys.argv[1]; nL = int(sys.argv[2]); nR = int(sys.argv[3])
    res, dt = solve(M, nL, nR)
    print(nL, nR, 'SAT' if res else 'UNSAT', '%.1fs' % dt)
    if res:
        print(json.dumps(res))
