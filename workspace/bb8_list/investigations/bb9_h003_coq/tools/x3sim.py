"""x3sim.py: literal simulator for X3 (and h003/M8/C04) on Kt/Kx-shaped tapes; prints B-at-right moments parsed as
Kx(tokens; m; r; t; far).  Library + CLI:  python x3sim.py K R t [frame] [nmom] [machine]"""
import idle, sys
X3 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_1RK1RC'
C04 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
H003 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC'
TB = [0, 0, 1, 1, 1, 1, 1, 1]
def parse(m):
    tr = {}
    for i, g in enumerate(m.split('_')):
        for c in (0, 1):
            x = g[3 * c:3 * c + 3]
            tr[(chr(65 + i), c)] = None if x[0] == '-' else (int(x[0]), 1 if x[1] == 'R' else -1, x[2])
    return tr
def tok(d): return [1] + [0, 1] * d
def kx_left(ds, m, r, t, far):
    """left stream nearest-first; ds = token values nearest-first; far = list (nearest-first) of the far end cells"""
    out = [1, 0, 0, 1] + TB * t + [1, 1] + [0, 1] * r + tok(m)
    for d in ds: out += tok(d)
    return out + far
STD = [1, 1]          # lft [] = 1 >> 1 >> const 0
class Sim:
    def __init__(self, m, left, state='B', pad=4096):
        self.tr = parse(m); n = len(left)
        self.t = bytearray(pad) + bytearray(reversed(left)) + bytearray(pad)
        self.pos = pad + n; self.q = state; self.steps = 0; self.halted = False
    def grow(self):
        if self.pos < 64:
            self.t[0:0] = bytearray(65536); self.pos += 65536
        if self.pos >= len(self.t) - 64:
            self.t.extend(bytearray(65536))
    def step(self):
        a = self.tr[(self.q, self.t[self.pos])]
        if a is None: self.halted = True; return False
        w, d, q = a; self.t[self.pos] = w; self.pos += d; self.q = q; self.steps += 1
        if self.pos < 64 or self.pos >= len(self.t) - 64: self.grow()
        return True
    def at_right(self):
        return self.q == 'B' and self.t[self.pos] == 0 and not any(self.t[self.pos:self.pos + 40]) and not any(self.t[self.pos:])
    def left_stream(self):
        L = self.t[max(0, self.pos - 400000):self.pos][::-1]
        i = len(L)
        while i > 0 and L[i - 1] == 0: i -= 1
        return list(L[:i])
def pkx(L):
    """parse a left stream nearest-first as Kx: returns (t, r, [m, tokens...], rest) or None"""
    if L[:4] != [1, 0, 0, 1]: return None
    i = 4; t = 0
    while L[i:i + 8] == TB: i += 8; t += 1
    if L[i:i + 2] != [1, 1]: return None
    i += 2; r = 0
    while L[i:i + 2] == [0, 1]: i += 2; r += 1
    toks = []
    while i < len(L) and L[i] == 1:
        i += 1; d = 0
        while L[i:i + 2] == [0, 1]: i += 2; d += 1
        toks.append(d)
    return t, r, toks, L[i:]
def rle(v, cap=40):
    """compress a token list (nearest-first) as far-first 'x*k' text"""
    v = list(reversed(v)); out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append('%d*%d' % (v[i], j - i) if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)
def moments(sim, nmax=10, maxsteps=10**8, filt=None):
    res = []
    while sim.steps < maxsteps and not sim.halted:
        if not sim.step(): break
        if sim.at_right():
            p = pkx(sim.left_stream())
            if filt is None or filt(p):
                res.append((sim.steps, p))
                if len(res) >= nmax: break
    return res
def fmt(p):
    if p is None: return 'unparsed'
    t, r, toks, rest = p
    return 't=%d r=%d far..near: %s | rest(near-first)=%s' % (t, r, rle(toks), ''.join(map(str, rest[:40])))
if __name__ == '__main__':
    K, R, t = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    nm = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    mach = {'X3': X3, 'C04': C04}[sys.argv[6]] if len(sys.argv) > 6 else X3
    left = kx_left([1] * K, 1, 3 * R + 2, t, STD)
    s = Sim(mach, left)
    for n, p in moments(s, nm, filt=lambda p: p is not None and p[1] == 2 and p[2][:1] == [1]):
        print(n, fmt(p))
    if s.halted: print('HALT', s.q, s.steps)

def is_cl(p):
    """a champion CL moment: m = 1, r = 3b+2, the nearest non-1 token a digit 3v+1, v >= 1"""
    if p is None: return None
    t, r, toks, rest = p
    if not toks or toks[0] != 1 or (r - 2) % 3: return None
    i = 1
    while i < len(toks) and toks[i] == 1: i += 1
    if i < len(toks) and toks[i] % 3 == 1 and toks[i] >= 4: return i
    return None
def is_top(p):
    if p is None: return False
    t, r, toks, rest = p
    return r == 2 and len(toks) >= 4 and toks[-3:] == [7, 0, 0] and all(x == 1 for x in toks[:-3]) and not rest
def walk(mach, left, Rs, maxcl=12, maxsteps=10**8, stop=is_top, verbose=True):
    """run; at each CL moment print it and jump with the next fake accumulator from Rs; stop at stop(p)"""
    s = Sim(mach, left); Rs = list(Rs); log = []; total = 0
    first = False
    while total < maxsteps:
        if not first and not s.step():
            log.append(('HALT', s.q, total + s.steps)); break
        first = False
        if s.at_right():
            p = pkx(s.left_stream())
            if stop(p):
                log.append(('STOP', total + s.steps, p)); break
            i = is_cl(p)
            if i is not None:
                t, r, toks, rest = p
                log.append(('CL', total + s.steps, p, i))
                if len(log) > maxcl or not Rs: break
                R = Rs.pop(0)
                toks2 = toks[:i] + [1] + toks[i + 1:]
                total += s.steps
                s = Sim(mach, kx_left(toks2[1:], 1, 3 * R + 2, t, rest)); first = True
    if verbose:
        for e in log:
            if e[0] == 'HALT': print('HALT', e[1], e[2])
            elif e[0] == 'STOP': print('%10d STOP %s' % (e[1], fmt(e[2])))
            else: print('%10d CL   %s  [v=%d j=%d b=%d]' % (e[1], fmt(e[2]), (e[2][2][e[3]] - 1) // 3, e[3] - 1, (e[2][1] - 2) // 3))
    return log

def pd0(L):
    """parse a left stream nearest-first as D0f t L P s y l: (t, L, P, y, s, rest) or None"""
    if L[:4] != [1, 0, 0, 1]: return None
    i = 4; t = 0
    while L[i:i + 8] == TB: i += 8; t += 1
    if L[i:i + 2] != [1, 1]: return None
    i += 2; n1 = 0
    while L[i:i + 1] == [1]: i += 1; n1 += 1
    P = 0
    while L[i:i + 3] == [0, 0, 1]: i += 3; P += 1
    if L[i:i + 3] != [1, 1, 0] or P == 0: return None
    i += 3; y = 0
    while L[i:i + 2] == [0, 1]: i += 2; y += 1
    if L[i:i + 3] != [1, 0, 1]: return None
    i += 3; s = 0
    while L[i:i + 2] == [0, 1]: i += 2; s += 1
    if L[i:i + 1] != [1]: return None
    return t, n1, P, y, s, L[i + 1:]
def d0walk(mach, left, nmax=4, maxsteps=10**8):
    s = Sim(mach, left); out = []
    while s.steps < maxsteps and len(out) < nmax:
        if not s.step(): out.append(('HALT', s.q, s.steps)); break
        if s.at_right():
            p = pd0(s.left_stream())
            if p: out.append((s.steps, p))
    return out
