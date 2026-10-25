"""Affine values over 'atoms' (huge quantities known by residue mod a modulus and by magnitude rank)."""
from fractions import Fraction as Fr
from math import gcd
from numth import *
import os
MB = 2**12 * 3**8 * 5**int(os.environ.get('MB5', 2)) * 7**2 * 11 * 13
ATOMS = {}   # id -> dict(name, res, mod, rank, note, geU)
_next = [0]
def new_atom(name, res, mod, rank=None, note='', geU=None):
    i = _next[0]; _next[0] += 1
    if rank is None: rank = max([a['rank'] for a in ATOMS.values()] + [0]) + 1
    ATOMS[i] = dict(name='%s#%d' % (name, i), res=res % mod, mod=mod, rank=rank, note=note, geU=geU)
    return Val(0, {i: 1})
class Val:
    __slots__ = ('c', 'co')
    def __init__(self, c=0, co=None):
        self.c = Fr(c); self.co = {k: Fr(v) for k, v in (co or {}).items() if v}
    @staticmethod
    def of(x): return x if isinstance(x, Val) else Val(x)
    def isconst(self): return not self.co
    def __add__(self, o):
        o = Val.of(o); co = dict(self.co)
        for k, v in o.co.items(): co[k] = co.get(k, 0) + v
        return Val(self.c + o.c, co)
    __radd__ = __add__
    def __neg__(self): return Val(-self.c, {k: -v for k, v in self.co.items()})
    def __sub__(self, o): return self + (-Val.of(o))
    def __rsub__(self, o): return Val.of(o) - self
    def __mul__(self, f):
        f = Fr(f); return Val(self.c * f, {k: v * f for k, v in self.co.items()})
    __rmul__ = __mul__
    def div(self, n): return self * Fr(1, n)
    def key(self): return (self.c, tuple(sorted(self.co.items())))
    def __eq__(self, o): return isinstance(o, Val) and self.key() == o.key() or (not isinstance(o, Val) and self.isconst() and self.c == o)
    def __hash__(self): return hash(self.key())
    def ival(self):
        assert self.isconst() and self.c.denominator == 1, self; return int(self.c)
    def at(self, reps):
        v = self.c + sum(v * reps[k] for k, v in self.co.items())
        assert v.denominator == 1, ('nonint', self, reps); return int(v)
    def res(self, m):
        """residue mod m (exact), raising if atom precision is insufficient"""
        D = self.c.denominator
        for v in self.co.values(): D = D * v.denominator // gcd(D, v.denominator)
        mm = m * D
        N = int(self.c * D)
        for k, v in self.co.items():
            a = ATOMS[k]
            if a['mod'] % mm: raise ValueError('precision: atom %s mod %d, need %d' % (a['name'], a['mod'], mm))
            N += int(v * D) * a['res']
        N %= mm
        if N % D: raise ValueError('nonintegral residue')
        return (N // D) % m
    def rank(self):
        return max([ATOMS[k]['rank'] for k in self.co] + [-1])
    def huge(self): return bool(self.co)
    def __repr__(self):
        if not self.co: return str(self.c)
        parts = []
        for k, v in sorted(self.co.items(), key=lambda kv: ATOMS[kv[0]]['rank']):
            nm = ATOMS[k]['name']
            parts.append(nm if v == 1 else '%s*%s' % (v, nm))
        if self.c: parts.append(str(self.c))
        return '(' + '+'.join(parts) + ')'
def best_res(v, mods=None):
    """residue with the largest modulus available among divisors MB / (2^j 3^i 5^l 7^c)"""
    cands = sorted(set(2 ** j * 3 ** i * 5 ** l * 7 ** c for j in range(6) for i in range(8) for l in range(8) for c in range(3)))
    for dv in cands:
        m = MB // dv
        if MB % dv:
            continue
        try:
            return v.res(m), m
        except ValueError:
            pass
    raise ValueError('no residue for %r' % v)
