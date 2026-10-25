"""coding.py (never_audit): digit codings on top of v-lists.
  V   : digits = v-entries themselves (1^d 0 coding).
  U10 : digits = runs of v-entries equal to 1 ((10)^d units), separated by single 0-entries (an extra 0 cell);
        the trailing fixed entries TF are raw v-entries (markers such as 2 = '11').
Both give K-configs  digits [d_1..d_n, A] + TF.  decode() accepts ints, Lin and ('blk', items, n) entries."""
from sym import Lin

class VCoding:
    name = 'V'
    def decode(self, v, nT):
        return list(v[:len(v) - nT]) if nT else list(v), list(v[len(v) - nT:]) if nT else []
    def encode(self, digits, TF, z, q):
        from sym import v_to_tokens
        return v_to_tokens(list(digits) + list(TF), z, q)

def _const(e):
    if isinstance(e, int): return e
    if isinstance(e, Lin) and e.isconst(): return int(e.const())
    return None

class U10Coding:
    name = 'U10'
    def __init__(self, sep=1, unit=1):
        self.sep = sep; self.unit = unit; self.name = ('U10' if unit == 1 else 'U110') + ('' if sep == 1 else 's%d' % sep)
    def decode(self, v, nT):
        body, tf = (list(v[:len(v) - nT]), list(v[len(v) - nT:])) if nT else (list(v), [])
        if all(type(e) is int for e in body):          # fast path for literal v-lists
            digs = []; cur = 0; zeros = 0; started = False
            for c in body:
                if c == self.unit:
                    if started and zeros >= 1:
                        if zeros % self.sep: raise ValueError('U10: separator width')
                        digs.append(cur); digs.extend([0] * (zeros // self.sep - 1)); cur = 0
                    started = True; zeros = 0; cur += 1
                elif c == 0: zeros += 1
                else: raise ValueError('U10: entry %r' % (c,))
            if started:
                digs.append(cur)
                if zeros:
                    if zeros % self.sep: raise ValueError('U10: separator width')
                    digs.extend([0] * (zeros // self.sep))
            return digs, tf
        digs = []; cur = Lin.c(0); zeros = 0; started = False
        def feed(e):
            nonlocal cur, zeros, started
            c = _const(e)
            if c == self.unit:
                if started and zeros >= 1:
                    if zeros % self.sep: raise ValueError('U10: separator width')
                    digs.append(cur); digs.extend([Lin.c(0)] * (zeros // self.sep - 1)); cur = Lin.c(0)
                started = True; zeros = 0; cur = cur + 1
            elif c == 0:
                zeros += 1
            else:
                raise ValueError('U10: entry %r' % (e,))
        for e in body:
            if isinstance(e, tuple):
                items, n = e[1], e[2]
                if all(_const(x) == self.unit for x in items):
                    if started and zeros >= 1:
                        if zeros % self.sep: raise ValueError('U10: separator width')
                        digs.append(cur); digs.extend([Lin.c(0)] * (zeros // self.sep - 1)); cur = Lin.c(0)
                    started = True; zeros = 0; cur = cur + n * len(items); continue
                # periodic block: copies 1,2 literal, copy 3 = steady emission, then n-3 more copies as a digit block
                for x in items: feed(x)
                for x in items: feed(x)
                before = len(digs); st = (cur, zeros, started)
                for x in items: feed(x)
                mid = digs[before:]; del digs[before:]; cur, zeros, started = st
                digs.append(('blk', mid, n - 2))
                continue
            feed(e)
        if started:
            digs.append(cur)
            if zeros:
                if zeros % self.sep: raise ValueError('U10: separator width')
                digs.extend([Lin.c(0)] * (zeros // self.sep))
        return digs, tf
    def encode(self, digits, TF, z, q):
        toks = []
        for i, d in enumerate(digits):
            if i > 0: toks.append('0' * self.sep)
            w = '1' * self.unit + '0'
            if isinstance(d, str): toks.append(w + '^' + d)
            elif d > 0: toks.append(w + '^%d' % d)
        # digits end with '...10'; TF entries follow (joined by single 0s, the first 0 is already there)
        for j, e in enumerate(TF):
            if j > 0: toks.append('0')
            if e > 0: toks.append('1^%d' % e)
            else: toks.append('0')
        s = ' '.join(toks)
        if not TF and z > 0: z -= 1          # the last '10' already ends with a 0 cell
        if z > 0: s += ' 0^%d' % z
        return s + ' ' + q + '>'

class ChampCoding:
    """champion-type coding: prefix '11', digits (10)^d separated by an extra '1'.  v-entries: 1 = unit,
    2 = separator + first unit of the next digit, e >= 3 inside = (e-2) zero digits; first entry 3 = prefix + unit."""
    name = 'C1'
    def decode(self, v, nT):
        body, tf = (list(v[:len(v) - nT]), list(v[len(v) - nT:])) if nT else (list(v), [])
        if not body or _const(body[0]) != 3: raise ValueError('C1: prefix')
        digs = []; cur = Lin.c(1)
        for e in body[1:]:
            if isinstance(e, tuple):
                items, n = e[1], e[2]
                if all(_const(x) == 1 for x in items): cur = cur + n * len(items); continue
                if all(_const(x) == 2 for x in items):   # n digits of one unit each
                    digs.append(cur); digs.append(('blk', [Lin.c(1)], n - 1)); cur = Lin.c(1); continue
                raise ValueError('C1: block %r' % (items,))
            c = _const(e)
            if c == 1: cur = cur + 1
            elif c is not None and c >= 2:
                digs.append(cur); digs.extend([Lin.c(0)] * (c - 2)); cur = Lin.c(1)
            else: raise ValueError('C1: entry %r' % (e,))
        digs.append(cur)
        return digs, tf
    def encode(self, digits, TF, z, q):
        toks = ['11']
        for i, d in enumerate(digits):
            if i > 0: toks.append('1')
            if isinstance(d, str): toks.append('10^' + d)
            elif d > 0: toks.append('10^%d' % d)
        for j, e in enumerate(TF):
            if e > 0: toks.append('1^%d' % e)
            if j < len(TF) - 1: toks.append('0')
        s = ' '.join(toks)
        if z > 0: s += ' 0^%d' % z
        return s + ' ' + q + '>'
