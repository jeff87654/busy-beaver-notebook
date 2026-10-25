# macro-level n-gram CPS over the canonical abstract system (L bit stack with T-run tokens, P, G gap stack with D-run tokens)
import sys, collections
kL, kG, K = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
B = 'B'
def cap(v): return v if v <= K else B
def norm(G):  # merge value 2 into D runs
    G = list(G); out = []
    for t in G:
        if t == 2: t = 'D'
        if t == 'D' and out and out[-1] == 'D': continue
        out.append(t)
    return tuple(out)
def trunc(w, k): return tuple(w[:k])
SL, SG = set(), set()
def addwins(S, w, k):
    # register all k-windows (or shorter ones ending with '$') of token tuple w
    for i in range(len(w)):
        x = w[i:i + k]
        if len(x) == k or (x and x[-1] == '$'): S.add(tuple(x))
def ext(S, w, k):
    """all windows w' of length k (or '$'-terminated) that extend prefix w (w is a window minus its first token)"""
    if w and w[-1] == '$': return [w]
    return [x for x in S if x[:len(w)] == w]
def popL(Lw):
    """yield (bit, newLw)"""
    t = Lw[0]
    if t == '$': yield 0, Lw; return
    if t in (0, 1):
        for x in ext(SL, Lw[1:], kL): yield t, x
        return
    # T run: pop bit 0, leaving 1 1 [T] rest
    for more in (True, False):
        nw = (1, 1) + (('T',) if more else ()) + Lw[1:]
        if len(nw) >= kL or nw[-1] == '$': yield 0, trunc(nw, kL)
def pushL(Lw, toks):
    w = tuple(Lw)
    for t in toks:
        if t == 'T' and w and w[0] == 'T': continue
        w = (t,) + w
    addwins(SL, w, kL)
    return trunc(w, kL)
def popG(Gw, n):
    """remove n leading tokens, re-extend windows"""
    rest = Gw[n:]
    if rest and rest[-1] == '$': return [rest]
    return [x for x in SG if x[:len(rest)] == rest]
def setfront(Gw, newfront):
    """replace first token by tokens newfront (tuple), normalize"""
    w = norm(newfront + Gw[1:])
    addwins(SG, w, kG)
    return trunc(w, kG)
def frontvals(Gw):
    """possible (value, Gw-with-front-removed-but-not-reextended prefix) for the front gap"""
    t = Gw[0]
    if t == '$': return [('INF', Gw)]  # INF: G empty
    if t == 'D':  # front 2, rest D^{>=0}
        return [(2, ('D',) + Gw[1:]), (2, Gw[1:] if len(Gw) > 1 else None)]
    return [(t, Gw[1:])]
def succ(c):
    Lw, P, Gw = c
    out = []
    if P in ('111', '011'):
        for x, Lw2 in popL(Lw):
            t = Gw[0]
            if t == '$': opts = [Gw]
            elif t == 'D':
                opts = []
                add = 1 if P == '111' else 2
                for rest in ([('D',) + Gw[1:]] + ([Gw[1:]] if len(Gw) > 1 else [])):
                    w = norm((cap(2 + add),) + tuple(rest)); addwins(SG, w, kG); opts.append(trunc(w, kG))
                # rest empty case handled via ext when Gw has length 1
                if len(Gw) == 1:
                    for x2 in popG(Gw, 1):
                        w = norm((cap(2 + add),) + x2); addwins(SG, w, kG); opts.append(trunc(w, kG))
            elif t == B: opts = [Gw]
            else:
                add = 1 if P == '111' else 2
                w = norm((cap(t + add),) + Gw[1:]); addwins(SG, w, kG); opts = [trunc(w, kG)]
            NP = ('111' if x else '011') if P == '111' else ('11' if x else '01')
            for g in opts:
                if len(g) < kG and g[-1] != '$':  # re-extend
                    for gg in popG(g, 0): out.append((Lw2, NP, gg))
                else: out.append((Lw2, NP, g))
        return out
    # consume: front D-run?
    m_opts = []
    if Gw[0] == 'D':
        for g in popG(Gw, 1): m_opts.append((True, g))
    else: m_opts.append((False, Gw))
    for m1, g in m_opts:
        h = g[0]
        if h == 'D': continue  # cannot happen after a maximal run
        for g2 in (popG(g, 1) if h != '$' else [g]):
            if P == '11':
                if h != '$' and h != B and h < 4: return None  # stuck
                hv = ['INF'] if h == '$' else ([cap(h - 3)] if h != B else [cap(v) for v in range(K - 2, K + 2)])
                Lw2 = pushL(Lw, (0,) + (('T',) if m1 else ()) + (1,))
                for v in hv:
                    w = g2 if v == 'INF' else norm((v,) + g2)
                    addwins(SG, w, kG); out.append((Lw2, '111', trunc(w, kG)))
            else:
                if h != '$' and h != B and h < 3: return None
                hv = ['INF'] if h == '$' else ([cap(h - 2)] if h != B else [cap(v) for v in range(K - 1, K + 2)])
                if m1: Lw2 = pushL(Lw, (0, 0, 'T', 1)); NP = '111'
                else: Lw2 = Lw; NP = '011'
                # m1 means m>=1; pushes 00 T^(m-1) 1: T^(m-1) may be empty
                Lws = [Lw2] + ([pushL(Lw, (0, 0, 1))] if m1 else [])
                for v in hv:
                    w = (0,) + (g2 if v == 'INF' else norm((v,) + g2))
                    addwins(SG, w, kG)
                    for L3 in Lws: out.append((L3, NP, trunc(w, kG)))
    return out
# start S(4): L empty, P=01, G=[2,2,2] -> (D, $)
L0 = ('$',); G0 = ('D', '$')
addwins(SL, L0, kL); addwins(SG, G0, kG)
start = (L0, '01', G0)
seen = {start}; Q = [start]; stuck = None; par = {start: None}
# iterate to fixpoint: windows sets grow, so repeat until no change
while True:
    nS = (len(SL), len(SG))
    i = 0
    Q = list(seen)
    while i < len(Q):
        c = Q[i]; i += 1
        r = succ(c)
        if r is None: stuck = c; break
        for d in r:
            if d not in seen: seen.add(d); Q.append(d); par[d] = c
        if len(seen) > 2000000: print('CAP'); sys.exit()
    if stuck: break
    if (len(SL), len(SG)) == nS: break

if stuck:
    c = stuck; path = []
    while c is not None: path.append(c); c = par[c]
    for c in reversed(path[:40]): print('   ', c)
print('STUCK at', stuck if stuck else None, 'configs', len(seen), 'SL', len(SL), 'SG', len(SG))
