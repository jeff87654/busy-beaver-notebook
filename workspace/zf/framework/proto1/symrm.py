"""Symbolic structured interpreter for the decision DAG of a Wade-framework .tm (register machine level).

Wff codes in this machine are astronomically large (nested Cantor pairs), so concrete unary execution of
even one main() iteration is impossible.  Values here are either Python ints (< BIG) or Big(tree, off)
= num(tree) + off with tree a Pair (structural: Cantor pairing is injective).  Acceleration:
  * nodes named pair(o,a,b).0 / unpair(o1,o2,i).0 are executed abstractly (their bodies are Wade's
    unchanged subroutines; checked against plain execution by selftest()),
  * nodes named if_eq(a,b,...).0 compare abstractly (zeroing both) and run the cdr (body) iff equal,
  * while loops (x.decnz, continue 1) and (x.decnz, (B, continue 2)) whose body B is straight-line incs are executed in bulk.
Everything else is executed one RM op at a time with the structured semantics of RM.v (run)."""
import sys, re, math
from dag import extract

BIG = 1 << 62


class Pair:
    __slots__ = ('a', 'b', 'h')

    def __init__(self, a, b):
        self.a = a; self.b = b; self.h = hash((a, b))

    def __eq__(self, o):
        return isinstance(o, Pair) and self.h == o.h and self.a == o.a and self.b == o.b

    def __hash__(self):
        return self.h

    def __repr__(self):
        return f'<{self.a!r}.{self.b!r}>'


class Big:
    __slots__ = ('t', 'off')

    def __init__(self, t, off=0):
        self.t = t; self.off = off

    def __eq__(self, o):
        return isinstance(o, Big) and self.off == o.off and self.t == o.t

    def __hash__(self):
        return hash((self.t, self.off))

    def __repr__(self):
        return f'{self.t!r}' + (f'{self.off:+d}' if self.off else '')


def isz(v):
    return isinstance(v, int) and v == 0


def cpair(x, y):
    """Cantor (x . y) = x + (x+y)(x+y+1)/2 on values."""
    if isinstance(x, int) and isinstance(y, int):
        s = x + y; v = x + s * (s + 1) // 2
        if v < BIG:
            return v
    for v in (x, y):
        if isinstance(v, Big) and v.off != 0:
            raise ValueError('pair of offset big value')
    return Big(Pair(x, y))


def cunpair(z):
    if isinstance(z, int):
        d = (math.isqrt(8 * z + 1) - 1) // 2
        x = z - d * (d + 1) // 2
        return x, d - x
    if z.off != 0:
        raise ValueError('unpair of offset big value')
    return z.t.a, z.t.b


def add(a, b):
    if isinstance(a, int) and isinstance(b, int):
        if a + b >= BIG:
            raise ValueError('int overflow')
        return a + b
    if isz(a):
        return b
    if isz(b):
        return a
    if isinstance(a, Big) and isinstance(b, int):
        return Big(a.t, a.off + b)
    if isinstance(b, Big) and isinstance(a, int):
        return Big(b.t, b.off + a)
    raise ValueError('sum of two big values')


def dec(v):
    if isinstance(v, int):
        return v - 1
    return Big(v.t, v.off - 1)


class Halt(Exception):
    pass


class SymRM:
    def __init__(self, path, accelerate=True):
        self.start, self.tbl, self.nodes, self.regidx = extract(path)
        self.nreg = len(self.regidx)
        self.ops = 0
        self.accel = {'pair': 0, 'unpair': 0, 'if_eq': 0, 'loop': 0}
        self.accelerate = accelerate
        self.loopinfo = {}
        if accelerate:
            for n in self.nodes:
                li = self.loop_pattern(n)
                if li:
                    self.loopinfo[n] = li

    def ri(self, name):
        return self.regidx[name]

    def straight_incs(self, e, acc):
        if e[0] == 'op' and e[2] == 'inc':
            acc.append(self.ri(e[1])); return True
        if e[0] == 'node':
            c, d = self.nodes[e[1]]
            return self.straight_incs(c, acc) and self.straight_incs(d, acc)
        return False

    def loop_pattern(self, n):
        car, cdr = self.nodes[n]
        if not (car[0] == 'op' and car[2] == 'decnz'):
            return None
        x = self.ri(car[1])
        if cdr == ('continue', 1):
            return (x, [])
        if cdr[0] != 'node':
            return None
        b, k = self.nodes[cdr[1]]
        if k != ('continue', 2):
            return None
        acc = []
        if not self.straight_incs(b, acc):
            return None
        if x in acc:
            return None
        return (x, acc)

    def run_edge(self, e, R):
        k = e[0]
        if k == 'node':
            return self.run_node(e[1], R)
        if k == 'op':
            self.ops += 1
            r = self.ri(e[1])
            if e[2] == 'inc':
                R[r] = add(R[r], 1); return ('N',)
            if isz(R[r]):
                return ('B', 1)
            R[r] = dec(R[r]); return ('N',)
        if k == 'break':
            return ('N',) if e[1] == 0 else ('B', e[1])
        if k == 'continue':
            return ('C', e[1])
        if k == 'halt':
            raise Halt()
        raise ValueError(e)

    def run_node(self, n, R):
        if self.accelerate:
            m = re.match(r'(pair|unpair|if_eq)\(([^,()]+),([^,()]+),([^,()]+)\)\.0$', n)
            if m:
                kind, a, b, c = m.groups()
                if kind == 'pair':      # out := (in1 . in2); zeros in1, in2 (requires out = 0)
                    o, i1, i2 = self.ri(a), self.ri(b), self.ri(c)
                    if not isz(R[o]):
                        raise ValueError('pair into nonzero out')
                    R[o] = cpair(R[i1], R[i2]); R[i1] = 0; R[i2] = 0
                    self.accel['pair'] += 1; return ('N',)
                if kind == 'unpair':    # (out1, out2) := unpair(in); zeros in (requires outs = 0)
                    o1, o2, i = self.ri(a), self.ri(b), self.ri(c)
                    if not (isz(R[o1]) and isz(R[o2])):
                        raise ValueError('unpair into nonzero out')
                    R[o1], R[o2] = cunpair(R[i]); R[i] = 0
                    self.accel['unpair'] += 1; return ('N',)
                if kind == 'if_eq':     # zeros in1, in2; runs body (cdr) iff they were equal
                    i1, i2 = self.ri(a), self.ri(b)
                    eq = R[i1] == R[i2]; R[i1] = 0; R[i2] = 0
                    self.accel['if_eq'] += 1
                    if not eq:
                        return ('N',)
                    return self.cdr_then(n, R)
            li = self.loopinfo.get(n)
            if li:
                x, targets = li
                v = R[x]
                if not isz(v):
                    for t in targets:
                        R[t] = add(R[t], v)
                    R[x] = 0
                self.accel['loop'] += 1
                return ('N',)
        car, cdr = self.nodes[n]
        while True:
            r = self.run_edge(car, R)
            if r[0] == 'B':
                if r[1] == 1:
                    return ('N',)
                return ('B', r[1] - 1)
            if r[0] == 'C':
                return r
            r = self.run_edge(cdr, R)
            if r[0] == 'N' or r[0] == 'B':
                return r
            if r[1] == 1:
                continue      # loop: re-run this node
            return ('C', r[1] - 1)

    def cdr_then(self, n, R):
        car, cdr = self.nodes[n]
        r = self.run_edge(cdr, R)
        if r[0] == 'N' or r[0] == 'B':
            return r
        if r[1] == 1:
            return self.run_node(n, R)
        return ('C', r[1] - 1)

    def main(self, R):
        """one iteration of main(); returns True if the machine halts."""
        try:
            r = self.run_node('main().0', R)
        except Halt:
            return True
        assert r == ('N',), r
        return False


def selftest(path, per=40, seed=1):
    """Check accelerated pair/unpair/if_eq/loop nodes against plain op-by-op execution on small values."""
    import random
    rng = random.Random(seed)
    S = SymRM(path)
    P = SymRM(path, accelerate=False)
    targets = [n for n in S.nodes if re.match(r'(pair|unpair|if_eq)\([^()]*\)\.0$', n)] + list(S.loopinfo)
    bad = 0; tested = 0
    for n in targets:
        for t in range(per):
            R = [rng.randrange(0, 12) for _ in range(S.nreg)]
            m = re.match(r'(pair|unpair|if_eq)\(([^,()]+),([^,()]+),([^,()]+)\)', n)
            if m:
                kind, a, b, c = m.groups()
                if kind == 'unpair':
                    R[S.ri(a)] = 0; R[S.ri(b)] = 0; R[S.ri(c)] = rng.randrange(0, 300)
                if kind == 'pair':
                    R[S.ri(a)] = 0
                if kind == 'if_eq' and rng.random() < 0.5:
                    R[S.ri(b)] = R[S.ri(a)]
            R1 = list(R); R2 = list(R)
            try:
                x1 = S.run_node(n, R1)
            except ValueError:
                continue
            x2 = P.run_node(n, R2)
            tested += 1
            if x1 != x2 or R1 != R2:
                bad += 1; print('SELFTEST MISMATCH', n, R, x1, R1, x2, R2)
    print('selftest: accelerated nodes', len(targets), 'cases', tested, 'mismatches', bad)
    return bad == 0


if __name__ == '__main__':
    selftest(sys.argv[1])
