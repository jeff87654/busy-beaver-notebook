"""Outliner experiments: alternative common-subsequence outlining for a fixed zfp config.
Cell model: after outlining, DAG states = distinct reachable suffixes (length >= 2) of all reachable
sequences (reduce_to_cons hash-conses the cdr chains)."""
import sys, json, copy
import zfp

def load(cfgpath):
    cfg = json.load(open(cfgpath))
    perm = {k: tuple(v) for k, v in cfg.get('perm', {}).items()}
    cls = zfp.make(cfg['clauses'], perm, cfg['opt'], cfg.get('vmap', {}), cfg.get('flips', {}))
    return cls, cfg['order']

def fresh(cls, order):
    z = cls(); z.debug = False; z.AXIOMORDER = list(order); z.main(); return z

def finish(z):
    for o in z.OPT:
        if o.startswith('dc'):
            z.DC_TOP = o.startswith('dcT'); z.dechain(int(o[3:] if z.DC_TOP else o[2:]))
    z.reduce_to_cons(); z.name_sequences(); z.generate(); z.tm.gc(); z.tm.statename = z.tm.start
    return zfp.count(z)

def roots(z):
    return z.find_seq("main().0")

def cells(seqs, root):
    """distinct suffixes of length >= 2 over sequences reachable from root (symbol ints = seq ids)"""
    seen = set(); st = [root]; suf = set()
    while st:
        i = st.pop()
        if i in seen: continue
        seen.add(i)
        s = seqs[i]
        for k in range(len(s) - 1):
            suf.add(s[k:])
        for v in s:
            if isinstance(v, int): st.append(v)
    return len(suf)

if __name__ == '__main__':
    cls, order = load(sys.argv[1])
    z = fresh(cls, order)
    z.breakout_common_subsequences()
    r = roots(z)
    print('cells after wade outline', cells([s.seq for s in z.sequences], r))
    print('total states', finish(z))

# ---------------- alternative outliner ----------------
from TMBuilder import Sequence
from collections import Counter

class G:
    """grammar: id -> tuple; canonical (no two ids with equal content among reachable)"""
    def __init__(self, z):
        self.root = roots(z)
        self.s = {}
        st = [self.root]
        while st:
            i = st.pop()
            if i in self.s: continue
            self.s[i] = z.sequences[i].seq
            st += [v for v in self.s[i] if isinstance(v, int)]
        self.next = len(z.sequences)
        self.canon()
    def copy(self):
        g = G.__new__(G); g.root = self.root; g.s = dict(self.s); g.next = self.next; return g
    def canon(self):
        while True:
            by = {}
            rep = {}
            for i in sorted(self.s):
                t = self.s[i]
                if t in by: rep[i] = by[t]
                else: by[t] = i
            if not rep: break
            for i in rep: del self.s[i]
            for i, t in self.s.items():
                if any(v in rep for v in t if isinstance(v, int)):
                    self.s[i] = tuple(rep.get(v, v) if isinstance(v, int) else v for v in t)
        # drop unreachable
        seen = set(); st = [self.root]
        while st:
            i = st.pop()
            if i in seen: continue
            seen.add(i); st += [v for v in self.s[i] if isinstance(v, int)]
        for i in list(self.s):
            if i not in seen: del self.s[i]
    def cells(self):
        suf = set()
        for t in self.s.values():
            for k in range(len(t) - 1): suf.add(t[k:])
        return len(suf)
    def occurrences(self, L):
        occ = {}
        for i, t in self.s.items():
            if len(t) <= L and not (len(t) == L): continue
            for o in range(len(t) - L + 1):
                occ.setdefault(t[o:o + L], []).append((i, o))
        return occ
    def apply(self, m):
        """outline m everywhere (non-overlapping, left to right, sequences longer than m)"""
        mid = None
        for i, t in self.s.items():
            if t == m: mid = i
        if mid is None:
            mid = self.next; self.next += 1; self.s[mid] = m
        L = len(m)
        for i in list(self.s):
            if i == mid: continue
            t = self.s[i]
            if len(t) <= L: continue
            out = []; k = 0; ch = False
            while k < len(t):
                if t[k:k + L] == m and len(t) > L:
                    out.append(mid); k += L; ch = True
                else:
                    out.append(t[k]); k += 1
            if ch: self.s[i] = tuple(out)
        self.canon()

def greedy(g, maxL=None, topT=60, minL=2, verbose=False):
    """repeatedly apply the repeated substring with the best exact cell gain"""
    cur = g.cells()
    while True:
        cands = Counter()
        Ls = range(minL, (maxL or max(len(t) for t in g.s.values())) + 1)
        for L in Ls:
            for m, occ in g.occurrences(L).items():
                if len(occ) >= 2:
                    cands[m] = (len(occ) - 1) * (L - 1)
        best = None
        for m, _ in cands.most_common(topT):
            h = g.copy(); h.apply(m); c = h.cells()
            if c < cur and (best is None or c < best[0]): best = (c, m, h)
        if not best: return g
        cur, m, g = best
        if verbose: print('apply', len(m), cur, flush=True)

def install(z, g):
    """write grammar g back into the builder z"""
    for i in range(len(z.sequences), g.next):
        z.sequences.append(Sequence(()))
    for i, t in g.s.items():
        z.sequences[i].seq = t
        z.sequence_lookup[t] = i
    return z

def rgreedy(g, rng, topT=40, mode='mix'):
    """randomized greedy: each step picks among improving candidates (exact gain), biased to the best"""
    cur = g.cells()
    while True:
        cands = Counter()
        maxL = max(len(t) for t in g.s.values())
        for L in range(2, maxL + 1):
            for m, occ in g.occurrences(L).items():
                if len(occ) >= 2:
                    cands[m] = (len(occ) - 1) * (L - 1) + (rng.random() * 3 if mode == 'mix' else 0)
        res = []
        for m, _ in cands.most_common(topT):
            h = g.copy(); h.apply(m); c = h.cells()
            if c < cur: res.append((c, rng.random(), m, h))
        if not res: return g
        res.sort(key=lambda r: (r[0], r[1]))
        k = 0
        while k + 1 < len(res) and rng.random() < 0.35: k += 1
        cur, _, m, g = res[k]

# ---------------- grammar ILS (inline k macros, re-outline greedily) ----------------
def is_site(e):
    return isinstance(e, str) and (e.startswith('_break') or e.startswith('_continue'))

def escapes(g):
    """ids whose subtree contains a break/continue site that escapes the id (dechain's esc rule)"""
    memo = {}
    def esc(v):
        if v in memo: return memo[v]
        sq = g.s[v]; n = len(sq); eb = ec = 10**9
        for i, e in enumerate(sq):
            car = 1 if i < n - 1 else 0; cdr = i if i < n - 1 else n - 1
            if isinstance(e, int):
                b, c = esc(e)
                if b < 0: eb = min(eb, b + car)
                if c < 0: ec = min(ec, c + cdr)
            elif e.startswith('_break.'):
                k = int(e.split('.')[1])
                if k > 0: eb = min(eb, car - k)
            elif e.startswith('_continue.'):
                ec = min(ec, cdr - int(e.split('.')[1]))
        memo[v] = (eb, ec); return memo[v]
    return {v for v in g.s if min(esc(v)) <= 0}

def safe_parent(g, p, esc):
    return all(not is_site(e) and not (isinstance(e, int) and e in esc) for e in g.s[p])

def inline(g, v, esc):
    """inline v into all its parents, if v has no escapes and every parent is safe; else no-op"""
    if v == g.root or v in esc: return False
    parents = [p for p, t in g.s.items() if v in t]
    if not parents or not all(safe_parent(g, p, esc) for p in parents): return False
    body = g.s[v]
    for p in parents:
        t = g.s[p]; out = []
        for e in t:
            if e == v: out.extend(body)
            else: out.append(e)
        g.s[p] = tuple(out)
    g.canon()
    return True

def safe_apply_ok(g, m, esc):
    return True   # outlining only rewrites sequences longer than m; checked in apply via safe_parent

def apply_safe(g, m, esc):
    mid = None
    for i, t in g.s.items():
        if t == m: mid = i
    if mid is None:
        mid = g.next; g.next += 1; g.s[mid] = m
    L = len(m)
    for i in list(g.s):
        if i == mid: continue
        t = g.s[i]
        if len(t) <= L or not safe_parent(g, i, esc): continue
        out = []; k = 0; ch = False
        while k < len(t):
            if t[k:k + L] == m:
                out.append(mid); k += L; ch = True
            else:
                out.append(t[k]); k += 1
        if ch: g.s[i] = tuple(out)
    g.canon()

def rgreedy_safe(g, rng, topT=40, noise=3.0):
    cur = g.cells(); esc = escapes(g)
    while True:
        cands = Counter()
        maxL = max(len(t) for t in g.s.values())
        for L in range(2, maxL + 1):
            occ = {}
            for i, t in g.s.items():
                if len(t) <= L or not safe_parent(g, i, esc): continue
                for o in range(len(t) - L + 1):
                    occ.setdefault(t[o:o + L], []).append((i, o))
            for m, oc in occ.items():
                if len(oc) >= 2 or any(m == t for t in g.s.values()):
                    cands[m] = (len(oc) - 1) * (L - 1) + rng.random() * noise
        res = []
        for m, _ in cands.most_common(topT):
            h = g.copy(); apply_safe(h, m, esc); c = h.cells()
            if c < cur: res.append((c, rng.random(), m, h))
        if not res: return g
        res.sort(key=lambda r: (r[0], r[1]))
        k = 0
        while k + 1 < len(res) and rng.random() < 0.35: k += 1
        cur, _, m, g = res[k]
        esc = escapes(g)
