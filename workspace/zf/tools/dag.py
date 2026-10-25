"""Extract the decision DAG from a Wade .tm file and simulate the register machine semantics atomically.

Node: name -> (car, cdr); edge = ('node', name) | ('op', regname, 'inc'|'decnz') | ('break', k) | ('continue', k) | ('halt',)
Path semantics (IP = list of bits, MSB first, implicit trailing zeros):
  advance:    P := P + 1 (binary increment; overflow gives an all-zero IP: the TM moves its marker left)
  break k:    strip bits from the right until k zeros removed, then increment
  continue k: strip bits from the right until k ones removed
  decnz on zero register: break 1
"""
import re, sys, json
sys.path.insert(0, 'tools')
from tmsim import load

def extract(path):
    start, tbl = load(path)
    names = sorted({s for (s, _) in tbl})
    dag = {s for s in names if not s[0].isdigit() and s != 'halt'}
    regs = []  # declaration order via 3.<reg>.inc chain: first reg goes to 1.inc on 1
    regstates = {s for s in names if s.startswith('3.')}
    # order: reg whose inc on 1 -> 1.inc is index 0; reg whose inc on 1 -> 3.<prev>.inc is next
    byinc = {}
    for s in regstates:
        if s.endswith('.inc'):
            w, d, n = tbl[(s, '1')]
            byinc[s] = n
    order = {}
    for s, n in byinc.items():
        if n == '1.inc': order[s] = 0
    changed = True
    while changed:
        changed = False
        for s, n in byinc.items():
            if s not in order and n in order:
                order[s] = order[n] + 1; changed = True
    regidx = {s[2:-4]: i for s, i in order.items()}
    def edge(w, d, n, side):
        if n in dag: return ('node', n)
        if n == 'halt': return ('halt',)
        if n.startswith('3.'):
            m = re.match(r'3\.(.*)\.(inc|decnz)$', n); return ('op', m.group(1), m.group(2))
        if n.startswith('6.break.'):
            j = int(n.split('.')[2]); return ('break', j + 1 if side == 0 else j)
        if n.startswith('6.continue.'):
            j = int(n.split('.')[2])
            if side == 0 and w == '1': return ('break', 0)   # _break.0 at car: (1,L,6.continue.0)
            return ('continue', j if side == 0 else j + 1)
        raise ValueError(n)
    nodes = {}
    for s in dag:
        w0, d0, n0 = tbl[(s, '0')]; w1, d1, n1 = tbl[(s, '1')]
        assert (d0 == 'R') == (n0 in dag or n0 == 'halt' or n0.startswith('3.')), (s, tbl[(s,'0')])
        nodes[s] = (edge(w0, d0, n0, 0), edge(w1, d1, n1, 1))
    return start, tbl, nodes, regidx

def walk(nodes, root, P):
    """Follow bits of P (0 beyond end) from root; return (leaf edge, depth d = number of bits consumed)."""
    cur = ('node', root); d = 0
    while cur[0] == 'node':
        b = P[d] if d < len(P) else 0
        cur = nodes[cur[1]][b]; d += 1
    return cur, d

def inc(P):
    P = list(P); i = len(P) - 1
    while i >= 0 and P[i] == 1: P[i] = 0; i -= 1
    if i >= 0: P[i] = 1
    # else: overflow (P was all ones). The TM moves its marker left and restarts with an all-zero IP,
    # which reads the same as the zeros now in P (RM.v: inc_rev [] = []).
    return P

def strip(P, bit, k):
    P = list(P)
    while k > 0:
        assert P, 'strip underflow'
        b = P.pop()
        if b == bit: k -= 1
    return P

class RM:
    def __init__(self, nodes, root, nregs):
        self.nodes = nodes; self.root = root; self.P = []; self.regs = [0] * nregs; self.halted = False
        self.ndecnz = 0
    def step(self, regidx):
        leaf, d = walk(self.nodes, self.root, self.P)
        # normalize stored path to walk depth (bits beyond must be 0)
        assert all(b == 0 for b in self.P[d:]), (self.P, d)
        P = (self.P + [0] * d)[:d]
        kind = leaf[0]
        if kind == 'halt': self.halted = True; return leaf
        if kind == 'op':
            r = regidx[leaf[1]]
            if leaf[2] == 'inc': self.regs[r] += 1; self.P = inc(P)
            else:
                self.ndecnz += 1
                if self.regs[r] > 0: self.regs[r] -= 1; self.P = inc(P)
                else: self.P = inc(strip(P, 0, 1))
        elif kind == 'break': self.P = inc(strip(P, 0, leaf[1]))
        elif kind == 'continue': self.P = strip(P, 1, leaf[1])
        return leaf

if __name__ == '__main__':
    start, tbl, nodes, regidx = extract(sys.argv[1])
    print('nodes', len(nodes), 'regs', regidx)
    from collections import Counter
    print(Counter(e[0] for n in nodes.values() for e in n))
    # max consecutive car edges
    def czeros(e):
        return 1 + czeros(nodes[e[1]][0]) if e[0] == 'node' else 0
    print('max consecutive zeros from any node', max(czeros(('node', n)) for n in nodes))
    def depth(n, seen={}):
        if n in seen: return seen[n]
        c, d = nodes[n]
        v = 1 + max(depth(c[1]) if c[0]=='node' else 0, depth(d[1]) if d[0]=='node' else 0)
        seen[n] = v; return v
    print('max depth', depth('main().0'))
