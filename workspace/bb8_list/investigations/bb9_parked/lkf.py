"""lkf.py: hybrid jump follower = Ligocki's macro simulator (chain steps + proof system, exact big integers) with
the JCL / JR1 jumps of pkf.cpp done at the canonical K-moments

    K = <far> D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 Q> 0^inf        (D(x) = (10)^x 1)

JCL  m = 1 mod 3, contiguous suffix of tokens = 1 mod 3 with a token > 1: all become D1, r := 3R+2 (R by policy).
JR1  m >= 3, m != 1 mod 3: (m, r) -> (m mod 3, 2^k (r+4) - 4), k = m // 3; exact when < 2^EXBITS, else a
     representative with the same residue mod MOD, size by policy.
Policies (fresh accumulator R):  --R N  (fixed)  |  --grow F  (R >= F * max(width, biggest token), >= --rmin)
     --cls C --mod M: R = C (mod M).  --B N: R of the first JCL.  --Rs a,b,c: explicit R list for the first JCLs.
K-moments are found by an exact base-level lookahead whenever the head is within the last blocks of the tape.
Output per jump: 'J# kind ... | near tokens (far->near)'.  HALT lines report an undefined slot read (literal).

  python lkf.py MACHINE [--R N | --grow F] [--B N] [--jumps N] [--loops N] [--bs 6] [--view N] [--time S] [--noprover]
"""
import sys, os, time, argparse
LIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'third_party', 'ligocki', 'Code')
sys.path.insert(0, os.path.abspath(LIG))
import IO
from Macro import Turing_Machine, Simulator
from Macro.Tape import Repeated_Symbol
from Macro.Turing_Machine import Block_Symbol, Simple_Machine_State
from NatExpr import InfNat

TAIL_UNIT = '11111100'
UR = '01'          # reversed digit unit (set from --u)
FINALC = [1, 0, 0, 1]


def parse_tm(m):
    rows = m.split('_'); T = {}
    for q, r in enumerate(rows):
        for c in (0, 1):
            x = r[3 * c:3 * c + 3]
            T[(q, c)] = None if ('-' in x or not ('A' <= x[2] <= chr(64 + len(rows)))) else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return len(rows), T


# ---------------- cell-level run-length lists: [(pattern, count)], far-left -> near-right -----------------
def norm(at):
    out = []
    for p, c in at:
        if c <= 0 or not p:
            continue
        if out and out[-1][0] == p:
            out[-1] = (p, out[-1][1] + c)
        else:
            out.append((p, c))
    return out


def alen(at):
    return sum(len(p) * c for p, c in at)


def cut_end(at, n):
    """drop the last n cells; returns new list"""
    at = list(at)
    while n > 0 and at:
        p, c = at[-1]; L = len(p) * c
        if L <= n:
            at.pop(); n -= L; continue
        # split this atom
        whole, rem = divmod(n, len(p))
        c2 = c - whole
        if rem:
            c2 -= 1
            at[-1] = (p, c2)
            at.append((p[:len(p) - rem], 1))
        else:
            at[-1] = (p, c2)
        n = 0
    return norm(at)


def split_end(at, n):
    """(prefix, suffix) with the suffix = the last n cells"""
    at = list(at); suf = []
    while n > 0 and at:
        p, c = at[-1]; L = len(p) * c
        if L <= n:
            at.pop(); suf.insert(0, (p, c)); n -= L; continue
        whole, rem = divmod(n, len(p))
        c2 = c - whole
        if rem:
            c2 -= 1; at[-1] = (p, c2); at.append((p[:len(p) - rem], 1)); suf.insert(0, (p[len(p) - rem:], 1))
        else:
            at[-1] = (p, c2)
        if whole:
            suf.insert(1 if rem else 0, (p, whole))
        n = 0
    return norm(at), norm(suf)


def take_end_cells(at, n):
    """split off (about) the last n cells as an explicit cell list; returns (rest_atoms, cells)"""
    at = list(at); cells = []
    while len(cells) < n and at:
        p, c = at[-1]
        if len(p) * c <= n - len(cells) + len(p) * 4 or c <= 4:
            at.pop(); cells = [int(ch) for ch in p * c] + cells
        else:
            k = max(1, (n - len(cells)) // len(p) + 1)
            at[-1] = (p, c - k); cells = [int(ch) for ch in p * k] + cells
    return norm(at), cells


class RevCursor:
    """reads the cell list from the right end leftwards (pattern strings are read reversed)"""

    def __init__(self, at):
        self.at = [(p[::-1], c) for p, c in reversed(at)]
        self.i = 0; self.off = 0      # off = cells consumed inside atom i
        self.pos = 0                  # cells consumed in total

    def _cell(self, i, off):
        p, c = self.at[i]
        return p[off % len(p)]

    def peek(self, n):
        s = []; i, off = self.i, self.off
        while len(s) < n and i < len(self.at):
            p, c = self.at[i]; L = len(p) * c
            while off < L and len(s) < n:
                s.append(p[off % len(p)]); off += 1
            if off >= L:
                i += 1; off = 0
        return ''.join(s)

    def adv(self, n):
        self.pos += n
        while n > 0 and self.i < len(self.at):
            p, c = self.at[self.i]; L = len(p) * c
            step = min(n, L - self.off); self.off += step; n -= step
            if self.off >= L:
                self.i += 1; self.off = 0

    def count_rep(self, u):
        """consume the maximal u^k; return k"""
        k = 0; lu = len(u)
        while True:
            if self.i < len(self.at):
                p, c = self.at[self.i]; L = len(p) * c
                rem = L - self.off
                if rem >= 4 * lu * len(p):
                    rot = (p[self.off % len(p):] + p[:self.off % len(p)])
                    blk = rot * (lu // len(p) + 1) if len(p) < lu else rot
                    # rot^* is a power of u iff rot*lu == u*len(rot) as strings (period check)
                    if (rot * lu) == (u * len(rot)):
                        # how many whole u fit in rem cells, keep alignment
                        q = rem // lu
                        k += q; self.adv(q * lu); continue
            if self.peek(lu) == u:
                self.adv(lu); k += 1
            else:
                return k


def rev_items(cur, nmax):
    """far view: items leftwards from the cursor: ('D', x) tokens or ('z', g) gaps; runs of equal items compressed"""
    items = []
    while len(items) < nmax:
        ch = cur.peek(1)
        if ch == '':
            break
        if ch == '1':
            # bulk path: a long run of identical whole tokens D(x) reversed = '1' + '01'*x
            cur.adv(1); x = cur.count_rep(UR); it = ('D', x)
        else:
            g = cur.count_rep('0'); it = ('z', g)
        if items and items[-1][0] == it:
            items[-1][1] += 1
        else:
            items.append([it, 1])
        # fast skip of long periodic runs of the same token: check pattern of the current atom
        if it[0] == 'D' and it[1] < 64 and cur.i < len(cur.at):
            p, c = cur.at[cur.i]; L = len(p) * c; rem = L - cur.off
            tokpat = ('1' + UR * it[1])
            if rem >= 8 * len(tokpat):
                rot = p[cur.off % len(p):] + p[:cur.off % len(p)]
                if rot * len(tokpat) == tokpat * len(rot):
                    q = rem // len(tokpat) - 1; cur.adv(q * len(tokpat)); items[-1][1] += q
    return items


def fmt_items(items):
    out = []
    for (kind, v), n in reversed(items):
        s = ('z%d' % v) if kind == 'z' else sh(v)
        out.append(s if n == 1 else '%s*%d' % (s, n))
    # compress repeated groups of 2..4 items: (a b)^k
    res = []; i = 0
    while i < len(out):
        best = None
        for L in (2, 3, 4):
            k = 1
            while out[i + k * L:i + (k + 1) * L] == out[i:i + L] and len(out[i:i + L]) == L:
                k += 1
            if k >= 3 and (best is None or k * L > best[0] * best[1]):
                best = (k, L)
        if best:
            k, L = best; res.append('(%s)^%d' % (' '.join(out[i:i + L]), k)); i += k * L
        else:
            res.append(out[i]); i += 1
    return ' '.join(res)


def to_blocks(at, bs):
    """cell atoms -> list of (block_string, count); the total length must be a multiple of bs"""
    out = []; buf = ''

    def emit(b, n):
        if out and out[-1][0] == b:
            out[-1] = (b, out[-1][1] + n)
        else:
            out.append((b, n))
    for p, c in at:
        L = len(p) * c
        if L <= 8 * bs + len(p) * 8:
            s = p * c
            buf += s
            while len(buf) >= bs:
                emit(buf[:bs], 1); buf = buf[bs:]
            continue
        # big atom: fill the buffer to a block boundary first
        idx = 0
        while buf:
            buf += p[idx % len(p)]; idx += 1
            if len(buf) == bs:
                emit(buf, 1); buf = ''
        rem = L - idx
        ph = idx % len(p)
        rot = p[ph:] + p[:ph]
        blk = (rot * (bs // len(rot) + 2))[:bs]
        if all(rot[j] == rot[(j + bs) % len(rot)] for j in range(len(rot))):
            nb = rem // bs
            emit(blk, nb)
            used = nb * bs
            buf = ''.join(rot[(used + j) % len(rot)] for j in range(rem - used))
        else:
            if rem > 10 ** 6:
                raise RuntimeError('cannot block atom %s^%d with bs %d' % (p, c, bs))
            s = ''.join(rot[j % len(rot)] for j in range(rem)); buf += s
            while len(buf) >= bs:
                emit(buf[:bs], 1); buf = buf[bs:]
    if buf:
        raise RuntimeError('length not a multiple of bs')
    return out


class Follower:
    def __init__(self, a):
        self.a = a
        self.mstr = a.machine
        self.ns, self.T = parse_tm(a.machine)
        self.bs = a.bs
        base = IO.get_tm(a.machine)
        self.base = base
        mach = Turing_Machine.Block_Macro_Machine(base, self.bs, max_sim_steps_per_symbol=10 ** 6) if self.bs > 1 else base
        self.mach = mach
        opts = Simulator.create_default_options()
        opts.prover = not a.noprover
        opts.recursive = a.recursive
        opts.compute_steps = True
        opts.verbose_simulator = False; opts.verbose_prover = False
        opts.quiet = True
        self.sim = Simulator.Simulator(mach, opts)
        self.zero = Block_Symbol((0,) * self.bs) if self.bs > 1 else 0
        self.nj = 0; self.ncl = 0; self.zs = []
        self.basesteps = 0
        self.skip_until = 0
        self.hist = {}; self.nextrap = 0; self.infq = False
        self.jhist = []; self.nskip = 0
        import random as _r; self.rng = _r.Random(a.rrand)
        self.Rs = [int(x) for x in a.Rs.split(',')] if a.Rs else []
        global UR, FINALC
        self.tm = dict(u=a.u, S1=a.S1, T=a.tunit if a.tunit != '-' else '', S2=a.S2 if a.S2 != '-' else '', beta=a.beta, rc=a.rc)
        UR = a.u[::-1]
        FINALC = [int(ch) for ch in (self.tm['S2'] or self.tm['S1'])]

    # --- Ligocki tape <-> cell atoms
    def sym_str(self, s):
        return ''.join(str(int(x)) for x in s) if self.bs > 1 else str(int(s))

    def left_atoms(self):
        t0 = self.sim.tape.tape[0]
        return norm([(self.sym_str(r.symbol), int(r.num)) for r in t0[1:]])

    def right_atoms(self):
        t1 = self.sim.tape.tape[1]
        return norm([(self.sym_str(r.symbol), int(r.num)) for r in reversed(t1[1:])])

    def install(self, left_atoms, state):
        """left content (ends at the head cell), head on the blank right of it, moving right, base state"""
        L = alen(left_atoms)
        pad = (-L) % self.bs
        at = norm([('0', pad)] + list(left_atoms))
        blocks = to_blocks(at, self.bs)
        # strip leading all-zero blocks
        while blocks and set(blocks[0][0]) == {'0'}:
            blocks.pop(0)
        mk = (lambda b: Block_Symbol(tuple(int(ch) for ch in b))) if self.bs > 1 else (lambda b: int(b))
        t0 = [Repeated_Symbol(self.zero, InfNat())] + [Repeated_Symbol(mk(b), n) for b, n in blocks]
        self.sim.tape.tape = [t0, [Repeated_Symbol(self.zero, InfNat())]]
        self.sim.tape.dir = Turing_Machine.RIGHT
        self.sim.dir = Turing_Machine.RIGHT
        self.sim.state = Simple_Machine_State(state)

    # --- lookahead at the right end
    def lookahead(self, smax=4000, wl=96):
        tp = self.sim.tape
        nfin = len(tp.tape[1]) - 1
        if nfin > 2:
            return None
        left = self.left_atoms(); right = self.right_atoms()
        rest, lc = take_end_cells(left, wl)
        if alen(right) > 4096:
            return None          # a long non-blank run right of the head: no K-moment inside this macro step
        rc = [int(ch) for p, c in right for ch in p * c]
        W = lc + rc
        h = len(lc) if tp.dir == Turing_Machine.RIGHT else len(lc) - 1
        s = int(self.sim.state)
        last1 = max([i for i, v in enumerate(W) if v] or [-1])
        QS = self.a.Q
        for n in range(smax):
            if h < 0:
                return ('X', n)
            while h >= len(W):
                W.append(0)
            c = W[h]
            if s == QS and c == 0 and h > last1 and h >= len(FINALC) and W[h - len(FINALC):h] == FINALC:
                if self.kjump(rest, W[:h], n):
                    return ('J',)
                # not a jump moment: keep looking (a later K-moment inside the same macro step must not be missed)
            tr = self.T[(s, c)]
            if tr is None:
                return ('H', rest, W, h, s, c, n)
            w, d, nx = tr
            W[h] = w
            if w and h > last1:
                last1 = h
            elif not w and h == last1:
                while last1 >= 0 and not W[last1]:
                    last1 -= 1
            h += d; s = nx
        return ('X', smax)        # no K-moment and no halt within smax exact steps: skip lookaheads for that long

    def pick(self, res, mod, width):
        a = self.a
        if self.ncl < len(self.Rs) and res is None:
            return self.Rs[self.ncl]
        if a.grow > 0:
            base = max(a.rmin, int(round(a.grow * 1000)) * width // 1000)
        else:
            base = a.R
        if res is not None:
            base += (res - base) % mod
        elif a.cls is not None:
            base += (a.cls - base) % a.mod
        elif a.rrand:
            base += self.rng.randrange(a.rrange)
        return base

    def kjump(self, rest, cells, nlook):
        """cells = explicit near cells ending at the head; rest = far atoms"""
        a = self.a
        at = norm(list(rest) + [(str(x), 1) for x in cells])
        cur = RevCursor(at)
        tm = self.tm
        if tm['S2']:
            if cur.peek(len(tm['S2'])) != tm['S2'][::-1]:
                return False
            cur.adv(len(tm['S2']))
        t = cur.count_rep(tm['T'][::-1]) if tm['T'] else 0
        if cur.peek(len(tm['S1'])) != tm['S1'][::-1]:
            return False
        cur.adv(len(tm['S1']))
        r = cur.count_rep(UR)
        rpos = cur.pos
        runs = []          # [x, n, end of the first token, end of the last token] (cells from the right end)
        while cur.peek(1) == '1' and len(runs) < 20000:
            cur.adv(1); x = cur.count_rep(UR); e = cur.pos
            if runs and runs[-1][0] == x:
                runs[-1][1] += 1; runs[-1][3] = e
            else:
                runs.append([x, 1, e, e])
            if x < 64 and cur.i < len(cur.at):          # bulk path over a long periodic run of equal tokens
                p, c = cur.at[cur.i]; rem = len(p) * c - cur.off; tp = '1' + UR * x
                if rem >= 8 * len(tp):
                    rot = p[cur.off % len(p):] + p[:cur.off % len(p)]
                    if rot * len(tp) == tp * len(rot):
                        # all but the last copy are complete tokens (the last one may continue past the atom)
                        q = rem // len(tp) - 1; cur.adv(q * len(tp)); runs[-1][1] += q; runs[-1][3] = cur.pos
        if not runs:
            return False
        if a.kdbg and self.nj >= a.kdbg:
            print('  KC nj=%d t=%d r=%s runs=%s' % (self.nj, t, sh(r), [(x, n) for x, n, e0, e1 in runs[:6]]))
        mm = runs[0][0]; kind = 0; k = 0; last = 0
        if mm % 3 == 1:
            nz = False; ntok = 0; j = 0
            while j < len(runs) and runs[j][0] % 3 == 1:
                nz = nz or runs[j][0] > 1; ntok += runs[j][1]; last = j; j += 1
            k = ntok - 1
            if nz:
                kind = 2
        elif mm >= 3:
            kind = 1
        if not kind:
            return False
        width = alen(at); big = max([x for x, n, e0, e1 in runs] + [r])
        if a.lskip and self.loopskip(at, runs, kind, k, t, rpos):
            return True
        if kind == 2:
            cut = runs[last][3]
            if self.ncl == 0 and a.B is not None:
                R = a.B
            else:
                R = self.pick(None, None, max(width, big))
            newr = 3 * R + tm['beta']; self.ncl += 1; self.zs.append(k)
            near = [(tm['u'] + '1', k + 1)]
            info = 'k=%d m=%s R=%d' % (k, sh(mm), R)
        else:
            cut = runs[0][2]
            k3, m2 = divmod(mm, 3)
            rc = tm['rc']
            if k3 + (r + rc).bit_length() <= 400 and (r + rc) * (1 << k3) - rc <= a.exactcap:
                newr = (r + rc) * (1 << k3) - rc; tag = ''
            else:
                res = (pow(2, k3, a.rmod) * ((r + rc) % a.rmod) - rc) % a.rmod
                base = max(a.rmin, int(round(a.grow * 1000)) * max(width, big) // 1000) if a.grow > 0 else a.rmin
                if a.rrand:
                    base += self.rng.randrange(max(1, a.rrange // a.rmod)) * a.rmod
                newr = base + (res - base) % a.rmod; tag = '(rep)'
            near = [(tm['u'], m2), ('1', 1)]
            info = 'm=%s->%d r=%s->%s%s' % (sh(mm), m2, sh(r), sh(newr), tag)
        # view of the far part + the rewritten tokens (far -> near)
        vc = RevCursor(at); vc.adv(rpos)
        items = rev_items(vc, a.view)
        self.nj += 1
        if self.nj == a.dumpj or a.dumpj == 0:
            print('DUMP ' + ''.join(p * c for p, c in at).lstrip('0'))
        print('J%d %s t=%d %s look=%d | %s' % (self.nj, 'CL' if kind == 2 else 'R1', t, info, nlook, fmt_items(items)), flush=True)
        newat = cut_end(at, cut) + near + [(tm['u'], newr), (tm['S1'], 1), (tm['T'], t), (tm['S2'], 1)]
        if self.nj == a.dumpj:
            print('POST ' + ''.join(p * c for p, c in norm(newat)).lstrip('0'))
        self.install(norm(newat), a.Q)
        return True


    # --- heuristic linear extrapolation (screening): a macro configuration that recurs with the same small symbols /
    # counts and big counts changing by constant deltas (3 consecutive recurrences, same loop gap) is advanced N periods.
    def sig(self):
        tp = self.sim.tape; cap = self.a.xcap
        key = [int(self.sim.state), tp.dir]; vals = []
        for side in (0, 1):
            key.append('|')
            for r in tp.tape[side][1:]:
                n = int(r.num)
                if n >= cap:
                    key.append((r.symbol, None)); vals.append(n)
                else:
                    key.append((r.symbol, n))
        return tuple(key), vals

    def extrap(self, loops):
        k, v = self.sig()
        if len(self.hist) > 20000:          # bound the history (it was the memory leak of the long runs)
            self.hist.clear()
        h = self.hist.setdefault(k, [])
        h.append((loops, v, self.sim.step_num))
        if len(h) > 4:
            h.pop(0)
        if len(h) < 4:
            return False
        (l0, v0, s0), (l1, v1, s1), (l2, v2, s2), (l3, v3, s3) = h
        if not (l1 - l0 == l2 - l1 == l3 - l2):
            return False
        d = [b - a for a, b in zip(v2, v3)]
        if d != [b - a for a, b in zip(v1, v2)] or d != [b - a for a, b in zip(v0, v1)] or not any(d):
            return False
        neg = [(x - 2 * self.a.xcap) // (-dx) for x, dx in zip(v3, d) if dx < 0]
        if not neg:
            print('INF? constant-growth recurrence (no decreasing count) after jump %d | %s' % (self.nj, self.view_now(self.a.view)), flush=True)
            self.infq = True
            return False
        N = min(neg)
        if N < 4:
            return False
        ds = s3 - s2
        i = 0; tp = self.sim.tape
        for side in (0, 1):
            for r in tp.tape[side][1:]:
                if int(r.num) >= self.a.xcap:
                    r.num = r.num + N * d[i]; i += 1
        self.sim.step_num += N * ds
        self.nextrap += 1; self.hist.clear()
        if self.a.vx:
            print('  X N=%d d=%s | %s' % (N, d, self.view_now(self.a.view)), flush=True)
        return True


    def loopskip(self, at, runs, kind, k, t, rpos):
        """jump-level loop acceleration: three consecutive jumps with the same kind/k/t, the same small tokens and the
        same far region, one single token decreasing by a constant d: advance that token by N periods (screening)."""
        a = self.a; T = a.bigt
        far = split_end(at, runs[-1][3])[0]
        fsig = tuple((p, c if c < T else ('*', c)) for p, c in far)
        sig = (kind, k, t, len(runs), tuple((x if x < T else '*', n) for x, n, e0, e1 in runs), fsig)
        h = self.jhist
        h.append((sig, [x for x, n, e0, e1 in runs]))
        if len(h) > 3:
            h.pop(0)
        if len(h) < 3 or not (h[0][0] == h[1][0] == h[2][0]):
            return False
        v0, v1, v2 = h[0][1], h[1][1], h[2][1]
        cand = [j for j in range(len(runs)) if runs[j][1] == 1 and v1[j] - v0[j] == v2[j] - v1[j] < 0 and v2[j] >= T]
        if not cand:
            return False
        j = cand[-1]; d = v1[j] - v2[j]; x = runs[j][0]
        N = (x - 12) // d - 2
        if N < 2:
            return False
        newx = x - N * d
        e = runs[j][2]; tl = 1 + len(self.tm['u']) * x
        pre = split_end(at, e)[0]
        keep = split_end(at, e - tl)[1]
        newat = norm(list(pre) + [(self.tm['u'], newx), ('1', 1)] + list(keep))
        self.install(newat, a.Q)
        self.jhist.clear(); self.nskip += 1
        print('  L skip run#%d %s -> %s (d=%d, N=%s) at jump %d' % (j, sh(x), sh(newx), d, sh(N), self.nj), flush=True)
        return True


    def dump_state(self, fn):
        import json
        tp = self.sim.tape
        d = dict(state=int(self.sim.state), dir=tp.dir, nj=self.nj, ncl=self.ncl,
                 left=[(self.sym_str(r.symbol), str(int(r.num))) for r in tp.tape[0][1:]],
                 right=[(self.sym_str(r.symbol), str(int(r.num))) for r in tp.tape[1][1:]])
        json.dump(d, open(fn, 'w'))

    def resume_state(self, fn):
        import json
        d = json.load(open(fn))
        mk = (lambda b: Block_Symbol(tuple(int(ch) for ch in b))) if self.bs > 1 else (lambda b: int(b))
        t0 = [Repeated_Symbol(self.zero, InfNat())] + [Repeated_Symbol(mk(b), int(n)) for b, n in d['left']]
        t1 = [Repeated_Symbol(self.zero, InfNat())] + [Repeated_Symbol(mk(b), int(n)) for b, n in d['right']]
        self.sim.tape.tape = [t0, t1]; self.sim.tape.dir = d['dir']; self.sim.dir = d['dir']
        self.sim.state = Simple_Machine_State(d['state']); self.nj = d['nj']; self.ncl = d['ncl']

    def view_now(self, n=60):
        at = norm(self.left_atoms() + self.right_atoms())
        return fmt_items(rev_items(RevCursor(at), n))

    def run(self):
        a = self.a; sim = self.sim; t0 = time.time(); loops = 0
        if a.resume:
            self.resume_state(a.resume)
        if a.kt:
            self.install(kt_atoms(a.kt, self.tm), a.Q)
        while True:
            if sim.op_state != Turing_Machine.RUNNING:
                print('SIMSTATE %s %s | %s' % (sim.op_state, sim.op_details, self.view_now(a.view)))
                return
            if time.time() - t0 > a.time:
                print('STOP loops=%d time=%.0f jumps=%d | %s' % (loops, time.time() - t0, self.nj, self.view_now(a.view)))
                if a.dumpstop:
                    self.dump_state(a.dumpstop)
                return
            la = None
            if (a.nolook < 0 or self.nj < a.nolook) and (a.noskip or sim.step_num >= self.skip_until):
                la = self.lookahead()
                if la is not None and la[0] == 'X':
                    self.skip_until = sim.step_num + la[1]; la = None
            if la is not None:
                if la[0] == 'H':
                    _, rest, W, h, s, c, n = la
                    print('HALT %s%d (literal, %d steps after lookahead start) jumps=%d | %s' % (chr(65 + s), c, n, self.nj,
                          fmt_items(rev_items(RevCursor(norm(list(rest) + [(str(x), 1) for x in W])), a.view))))
                    return
                if la[0] == 'J':
                    self.hist.clear(); self.skip_until = 0
                    if self.nj >= a.jumps:
                        print('END jumps %d extrap %d lskip %d' % (self.nj, self.nextrap, self.nskip)); return
                    continue
            sim.step(); loops += 1
            if sim.op_state == Turing_Machine.UNDEFINED:
                print('HALT(macro) %s | jumps=%d | %s' % (sim.op_details, self.nj, self.view_now(a.view)))
                return
            if sim.op_state != Turing_Machine.RUNNING:
                continue
            if a.xcap and self.extrap(loops):
                self.skip_until = 0
            if loops % 200 == 0:
                if a.maxmem and loops % 2000 == 0 and rss_gb() > a.maxmem:
                    print('STOP(mem %.1f GB) loops=%d time=%.0f jumps=%d' % (rss_gb(), loops, time.time() - t0, self.nj), flush=True)
                    return
                if a.loops and loops >= a.loops or time.time() - t0 > a.time:
                    print('STOP loops=%d time=%.0f jumps=%d | %s' % (loops, time.time() - t0, self.nj, self.view_now(a.view)))
                    return
                if a.snap and loops % a.snap == 0:
                    print('  SNAP loops=%d | %s' % (loops, self.view_now(a.view)), flush=True)


def kt_atoms(spec, tm):
    """--kt "items;m;r;t": far-first items (token d, d*k = k copies, zN = N blank cells), then D(m) (10)^r S1 T^t S2,
    as run-length cell atoms (huge counts stay symbolic)"""
    items, m, r, t = spec.split(';')
    at = []
    for it in [x for x in items.split(',') if x]:
        x, _, k = it.partition('*'); k = int(k) if k else 1
        if x.startswith('z'):
            at.append(('0', int(x[1:]) * k)); continue
        d = int(x)
        if k == 1 or d > 8:
            for _ in range(k if d <= 8 else 1):
                at += [('10', d), ('1', 1)]
            if d > 8 and k > 1:
                at += [('10' * d + '1', k - 1)]
        else:
            at.append(('10' * d + '1', k))
    at += [('10', int(m)), ('1', 1), ('10', int(r)), (tm['S1'], 1), (tm['T'], int(t)), (tm['S2'], 1)]
    return norm(at)


def rss_gb():
    """working set of this process in GB (Windows; 0 elsewhere)"""
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + \
                       [(n, ctypes.c_size_t) for n in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
                        'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage',
                        'PeakPagefileUsage')]
        c = PMC(); c.cb = ctypes.sizeof(PMC)
        k32 = ctypes.WinDLL('kernel32'); ps = ctypes.WinDLL('psapi')
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        ps.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        ps.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
        return c.WorkingSetSize / 2 ** 30
    except Exception:
        return 0.0


def sh(x):
    s = str(x)
    return s if len(s) <= 24 else '~%de%d' % (int(s[0]), len(s) - 1)


def main():
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)   # IDLE
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('--R', type=int, default=6)
    ap.add_argument('--grow', type=float, default=0)
    ap.add_argument('--rmin', type=int, default=20)
    ap.add_argument('--B', type=int, default=None)
    ap.add_argument('--Rs', default='')
    ap.add_argument('--cls', type=int, default=None)
    ap.add_argument('--mod', type=int, default=2520 * 11 * 13)
    ap.add_argument('--exactcap', type=int, default=10 ** 6)
    ap.add_argument('--rmod', type=int, default=36)
    ap.add_argument('--jumps', type=int, default=100)
    ap.add_argument('--loops', type=int, default=0)
    ap.add_argument('--time', type=float, default=3600)
    ap.add_argument('--bs', type=int, default=6)
    ap.add_argument('--Q', type=lambda s: ord(s) - 65, default=1)
    ap.add_argument('--u', default='10')
    ap.add_argument('--S1', default='11')
    ap.add_argument('--tunit', default='11111100')
    ap.add_argument('--S2', default='1001')
    ap.add_argument('--beta', type=int, default=2)
    ap.add_argument('--rc', type=int, default=4)
    ap.add_argument('--tmpl', default='', help='zfg template string; sets Q/u/S1/beta/rc for u=01 families (no tail)')
    ap.add_argument('--view', type=int, default=40)
    ap.add_argument('--snap', type=int, default=0)
    ap.add_argument('--noprover', action='store_true')
    ap.add_argument('--nolook', type=int, default=-1)
    ap.add_argument('--dumpj', type=int, default=-1)
    ap.add_argument('--noskip', action='store_true')
    ap.add_argument('--kdbg', type=int, default=0)
    ap.add_argument('--rrange', type=int, default=60)
    ap.add_argument('--dumpstop', default='')
    ap.add_argument('--resume', default='')
    ap.add_argument('--kt', default='', help='start at a Kt config "items;m;r;t" (see kt_atoms) instead of the blank tape')
    ap.add_argument('--rrand', type=int, default=0, help='seed: add a random offset to every fresh representative')
    ap.add_argument('--xcap', type=int, default=0)
    ap.add_argument('--lskip', action='store_true')
    ap.add_argument('--bigt', type=int, default=200)
    ap.add_argument('--vx', action='store_true')
    ap.add_argument('--recursive', action='store_true')
    ap.add_argument('--maxmem', type=float, default=4.0, help='stop when the working set exceeds this many GB (0 = off)')
    a = ap.parse_args()
    if a.tmpl:
        f = a.tmpl.split(',')
        a.Q = ord(f[1][0]) - 65; a.u = f[3][2:]; S = f[7][2:]
        a.beta = int(f[6].split('+')[1])
        if a.u == '10' and S.endswith('1001'):
            a.S1, a.S2, a.tunit = S[:-4], '1001', '11111100'; a.rc = 4
        else:
            a.S1, a.S2, a.tunit = S, '', ''; a.rc = 5 if a.u == '01' else a.rc
    Follower(a).run()


if __name__ == '__main__':
    main()
