"""ZF machine program with per-clause parameter-role permutations and optional program changes.

Clause specs are postfix token lists over roles a, b, c (proof-step parameters), constants v0..v3, wff
builders, and special blocks.  PERM[name] maps roles (a, b, c) -> parameter registers (1, 2, 3).
For every clause the SET of instances generated as (p1, p2, p3) ranges over N^3 is independent of the
permutation, so the theorem set of the enumerator (and the formal system) is unchanged."""
import zf2
from TMBuilder import subroutine
import TMBuilder

SPEC = {
    'B1':  'a b wim b c wim a c wim wim wim',
    'B2':  'a wn a wim a wim',
    'B3':  'a a wn b wim wim',
    # BY = CpCCNqCCqrNpq: a -> ((-.b -> ((b -> c) -> -.a)) -> b); with B1 it replaces B2 and B3 (zf/prune)
    'Y_CpCCNqCCqrNpq': 'a b wn b c wim a wn wim wim b wim wim',
    'B4':  'a b c wim wal a b wal a c wal wim wim',
    'B6b': 'a b c wal wal b a c wal wal wim',
    'B8b': 'a b weq a c wel b c wel wim wim',
    'B6a': 'a b weq c a b weq wal wim a b wel c a b wel wal wim wa',   # + check c != a, c != b
    'B6c': 'a a b wal wex b wim',
    'B7':  'a a b weq wex',
    'B8a': 'a b weq a c weq b c weq wim wim',
    'B8c': 'a b weq c a wel c b wel wim wim',
    'EXT': 'v2 v2 v0 wel v2 v1 wel wim v2 v1 wel v2 v0 wel wim wa wal v0 v1 weq wim',
    'REP': 'v3 v1 v2 v1 a wal v2 v1 weq wim wal wex wal v1 v2 v2 v1 wel v3 v3 v0 wel v1 a wal wa wex wim '
           'v3 v3 v0 wel v1 a wal wa wex v2 v1 wel wim wa wal wex wim',
    'POW': 'v1 v2 v3 v3 v2 wel v3 v0 wel wim wal v2 v1 wel wim wal wex',
    'UNI': 'v1 v2 v3 v2 v3 wel v3 v0 wel wa wex v2 v1 wel wim wal wex',
    'INF': 'v1 v0 v1 wel v0 v0 v1 wel v2 v2 v1 wel v1 v1 v2 wel v1 v0 weq wim v1 v0 weq v1 v2 wel wim wa wal '
           'wa wex wim wal wa wex',
    'DET': None, 'GEN': None,
    # Track B (propositionally equivalent merges of clauses with a common antecedent)
    'B8bc':  'a b weq a c wel b c wel wim c a wel c b wel wim wa wim',
    'B8abc': 'a b weq a c weq b c weq wim a c wel b c wel wim c a wel c b wel wim wa wa wim',
}
BASE = ['DET','GEN','B1','B2','B3','B4','B6b','B8b','B6a','B6c','B7','B8a','B8c','EXT','REP','POW','UNI','INF']
PREMISE = {'DET', 'GEN'}
ID = (1, 2, 3)

class ZFP(zf2.ZF2):
    CLAUSES = BASE
    PERM = {}
    FLIPS = {}     # closed clauses: operand-swap bitmask (forms.py)
    VMAP = {}      # closed clauses: variable renaming v_i -> v_VMAP[i] (Track B: changes the axiom formula)
    OPT = frozenset()

    def v_4(self):
        return zf2.ZF2.v_4(self)

    def preg(self, i):
        return {1: self.param1, 2: self.param2, 3: self.param3}[i]

    def parx(self, i):
        return {1: self.par1, 2: self.par2, 3: self.par3}[i]()

    def tok(self, t, perm, vmap=(0, 1, 2, 3)):
        if t in 'abc': return self.parx(perm['abc'.index(t)])
        if t[0] == 'v': return getattr(self, 'v_' + t[1:])()
        return getattr(self, t)()

    def clause(self, name):
        perm = self.PERM.get(name, ID)
        s1, s2, s3, tw = self.scratch1, self.scratch2, self.scratch3, self.topwff
        W = self.while_decnz
        select = self.select()
        if name == 'DET':
            # roles: a = ps (result), b = major premise, c = minor premise
            pa, pb, pc = (self.preg(i) for i in perm)
            cp_a = [W(pa, [tw.inc, s1.inc]), W(s1, pa.inc)] if 'cpord' in self.OPT else                    [W(pa, [s1.inc, tw.inc]), W(s1, pa.inc)]
            if 'detS3' in self.OPT and 'detswap' in self.OPT:   # major premise on top of the stack
                return [self.cparam(s3), self.cparam(pc), self.parx(perm[2]), self.parx(perm[0]), self.wim(),
                        W(tw, s2.inc), self.if_eq(s2, s3, cp_a), select]
            if 'detS3' in self.OPT:   # major premise popped straight into scratch3 (role b unused)
                return [self.cparam(pc), self.cparam(s3), self.parx(perm[2]), self.parx(perm[0]), self.wim(),
                        W(tw, s2.inc), self.if_eq(s2, s3, cp_a), select]
            return [self.cparam(pc), self.cparam(pb), self.parx(perm[2]), self.parx(perm[0]), self.wim(),
                    W(tw, s2.inc), W(pb, [s1.inc, s3.inc]), W(s1, pb.inc),
                    self.if_eq(s2, s3, cp_a),
                    select]
        if name == 'GEN':
            # roles: a = variable, c = premise
            pc = self.preg(perm[2])
            if 'genS3' in self.OPT:   # premise popped into scratch3 and pushed from there
                return [self.cparam(s3), self.parx(perm[0]), self.pushwff(), W(s3, tw.inc), self.wal(), select]
            return [self.cparam(pc), self.parx(perm[0]), self.parx(perm[2]), self.wal(), select]
        if name in self.VMAP or name in self.FLIPS or name not in SPEC:
            import forms
            toks = forms.postfix(forms.variant(forms.TREES[name], tuple(self.VMAP.get(name, (0, 1, 2, 3))),
                                               self.FLIPS.get(name, 0)))
        else:
            toks = SPEC[name].split()
        body = [self.tok(t, perm) for t in toks]
        if name == 'B6a':
            pa, pb, pc = (self.preg(i) for i in perm)
            Z = W(tw, ())
            if 'b6aS' in self.OPT:
                # saturating-subtraction test (destructive like b6aD): a+1-c, b+1-c (saturated at 0);
                # the test value is 1 iff a == c (resp. b == c)
                def sdec(p): return self.label("s", [p.decnz, "break_s"])
                def T(p): return self.label("t", [p.decnz, [[p.decnz, [W(p, ()), "break_t"]], Z]])
                body += [pa.inc, pb.inc, W(pc, [sdec(pa), sdec(pb)]), T(pa), T(pb)]
            elif 'b6aD' in self.OPT:
                # destructive check (B6a must be followed only by parameter-free clauses):
                # leaves param1..3 = 0, so main() need not zero them.
                body += [W(pc, [s1.inc, s3.inc]), W(pa, s2.inc), self.if_eq(s2, s3, [Z]),
                         W(s1, s3.inc), W(pb, s2.inc), self.if_eq(s2, s3, [Z])]
            else:
                body += [
                    W(pa, [s1.inc, s2.inc]), W(s1, pa.inc), W(pc, [s1.inc, s3.inc]), W(s1, pc.inc),
                    self.if_eq(s2, s3, [Z]),
                    W(pb, [s1.inc, s2.inc]), W(s1, pb.inc), W(pc, [s1.inc, s3.inc]), W(s1, pc.inc),
                    self.if_eq(s2, s3, [Z])]
        return body + [select]

    @subroutine
    def main(self):
        AXIOMS = self.axioms()
        if not self.AXIOMORDER:
            self.AXIOMORDER = list(range(len(AXIOMS)))
        W = self.while_decnz
        s1, s2 = self.scratch1, self.scratch2
        pl = self.prooflist
        zero = [W(self.axiomcode, ())]
        if 'b6aD' not in self.OPT and 'b6aS' not in self.OPT:
            zero += [W(self.param1, ()), W(self.param2, ()), W(self.param3, ())]
        dec = []
        for r in (self.axiomcode, self.param1, self.param2, self.param3):
            dec += [self.unpair(s1, s2, pl), W(s2, pl.inc), W(s1, r.inc)]
        return [
            self.if_not_decnz(pl, [W(self.nextproof, [s1.inc, pl.inc]), W(s1, self.nextproof.inc),
                                   self.nextproof.inc]),
            *zero, *dec,
            self.v_0(),
            *[v for i in self.AXIOMORDER for v in AXIOMS[i]],
            [self.topwff.decnz,
             self.label("if", [[self.topwff.decnz, [[self.topwff.inc, self.topwff.inc], "break_if"]], "halt"])]
        ]

    # --- optional wff-builder variants (same wff codes) ---
    def tagk(self, k):
        # tw := (tw . k) without a stack round trip: s1 := tw; tw := k; tw := (s1 . tw)
        tw = self.topwff
        incs = [tw.inc] * k
        return [self.while_decnz(tw, self.scratch1.inc), *incs,
                self.pair(self.scratch2, self.scratch1, tw), self.while_decnz(self.scratch2, tw.inc)]

    def wn(self):
        if 'tagwn' in self.OPT or 'tagall' in self.OPT or 'fuse' in self.OPT:
            return self._sub('wn', self.tagk(3))
        return zf2.ZF2.wn(self)

    def bink(self, k):
        # tw := ((pop . tw) . k): cons, but the cons result goes straight to scratch1 for the tag pairing
        s1, s2, tw, ws = self.scratch1, self.scratch2, self.topwff, self.wffstack
        W = self.while_decnz
        return [self.unpair(s1, s2, ws), W(s2, ws.inc), self.pair(s2, s1, tw), W(s2, s1.inc),
                *([tw.inc] * k), self.pair(s2, s1, tw), W(s2, tw.inc)]

    def weq(self):
        if 'fuse' in self.OPT: return self._sub('weq', self.bink(0))
        if 'tagall' in self.OPT: return self._sub('weq', [self.cons(), *self.tagk(0)])
        return zf2.ZF2.weq(self)

    def wel(self):
        if 'fuse' in self.OPT: return self._sub('wel', self.bink(1))
        if 'tagall' in self.OPT: return self._sub('wel', [self.cons(), *self.tagk(1)])
        return zf2.ZF2.wel(self)

    def wim(self):
        if 'fuse' in self.OPT: return self._sub('wim', self.bink(2))
        if 'tagall' in self.OPT: return self._sub('wim', [self.cons(), *self.tagk(2)])
        return zf2.ZF2.wim(self)

    def wal(self):
        if 'fuse' in self.OPT: return self._sub('wal', self.bink(4))
        if 'tagall' in self.OPT: return self._sub('wal', [self.cons(), *self.tagk(4)])
        return zf2.ZF2.wal(self)

    def _sub(self, name, body):
        # emulate @subroutine for a named builder
        key = (name + '!',)
        if key in self.memo: return self.memo[key]
        rv = tuple(v for v in (self.add_sequence(v2) for v2 in body) if v != ())
        self.memo[key] = rv
        i = self.add_sequence(rv)
        if self.sequences[i].name is None: self.sequences[i].name = name + '().0'
        return rv

    def select(self):
        if 'sel2' not in self.OPT and 'sel3' not in self.OPT:
            return zf2.ZF2.select(self)
        return self._select2()

    def _select2(self):
        # ac > 0 (decremented): keep the built wff, drop the previous one; ac == 0: drop the built wff,
        # pop the previous one back into topwff.  Same effect as zf2.py's select.
        s1, s2, tw, ws = self.scratch1, self.scratch2, self.topwff, self.wffstack
        W = self.while_decnz
        if 'sel3' in self.OPT:     # pop the previous wff via scratch1 (shares the unpair(s1,s2,ws) instance)
            return [self.label("fn", [
                [self.axiomcode.decnz, [[self.unpair(s1, s2, ws), W(s2, ws.inc), W(s1, ())], "break_fn"]],
                [W(tw, ()), self.unpair(s1, s2, ws), W(s2, ws.inc), W(s1, tw.inc)]])]
        return [self.label("fn", [
            [self.axiomcode.decnz, [[self.unpair(s1, s2, ws), W(s2, ws.inc), W(s1, ())], "break_fn"]],
            [W(tw, ()), self.unpair(tw, s2, ws), W(s2, ws.inc)]])]
    _select2.__name__ = 'select'
    _select2 = subroutine(_select2)

    @subroutine
    def cparam(self, p):
        """if axiomcode == 1 (this clause is the selected one): p := pop(wffstack).  (zf2.py's cparam;
        with OPT cp3 the target scratch3 is known to be 0, so the zeroing loop is omitted.)"""
        ac = self.axiomcode
        setp = self.while_decnz(self.scratch1, p.inc) if ('cp3' in self.OPT and p == self.scratch3) else             [self.while_decnz(p, ()), self.while_decnz(self.scratch1, p.inc)]
        return [
            self.label("fn", [
                self.label("test", [
                    self.label("innertest", [
                        ac.decnz,
                        [[ac.decnz, [[ac.inc, ac.inc], "break_innertest"]],
                         [[ac.inc, self.unpair(self.scratch1, self.scratch2, self.wffstack),
                           self.while_decnz(self.scratch2, self.wffstack.inc)],
                          "break_test"]]]),
                    "break_fn"]),
                setp])]

    @subroutine
    def pushwff(self):
        s1, s2, tw, ws = self.scratch1, self.scratch2, self.topwff, self.wffstack
        W = self.while_decnz
        if 'push2' in self.OPT:   # same effect, via the pair(s2, s1, tw) instance used by cons/tags
            return [W(tw, s1.inc), W(ws, tw.inc), self.pair(s2, s1, tw), W(s2, ws.inc)]
        return [self.pair(s1, tw, ws), W(s1, ws.inc)]

    def if_eq(self, in1, in2, body):
        if 'ifeq2' not in self.OPT:
            return zf2.ZF2.if_eq(self, in1, in2, body)
        return self._if_eq2(in1, in2, body)

    def _if_eq2(self, in1, in2, body):
        # zf2.py's if_eq leaves the loop with break level 2 when in1 > in2; here that case zeroes in1 and
        # sets in2 := 1, so the common in2 != 0 exit handles it: no 6.break.2 framework state needed.
        return [self.label("fn", [
            [self.label("loop", [in1.decnz, [[in2.decnz, "continue_loop"], [self.while_decnz(in1, ()), in2.inc]]]),
             [in2.decnz, [self.while_decnz(in2, ()), "break_fn"]]],
            body])]

    _if_eq2.__name__ = 'if_eq'
    _if_eq2 = subroutine(_if_eq2)

    def dechain(self, D):
        """Inline pure (control-flow-closed) sequences on car chains until every chain of consecutive car
        edges is <= D (fewer 4.dispatch states).  Inlining a sequence whose breaks/continues all stay inside
        it is semantics-preserving.  Raises AssertionError if impossible."""
        seqs = self.sequences
        memo_e = {}
        def esc(v):
            if v in memo_e: return memo_e[v]
            sq = seqs[v].seq; n = len(sq); eb = ec = 10**9
            for i, e in enumerate(sq):
                car = 1 if i < n - 1 else 0; cdr = i if i < n - 1 else n - 1
                if isinstance(e, int):   # only control flow escaping e matters here
                    b, c = esc(e)
                    if b < 0: eb = min(eb, b + car)
                    if c < 0: ec = min(ec, c + cdr)
                elif e.startswith('_break.'):
                    k = int(e.split('.')[1])
                    if k > 0: eb = min(eb, car - k)
                elif e.startswith('_continue.'):
                    ec = min(ec, cdr - int(e.split('.')[1]))
            memo_e[v] = (eb, ec); return memo_e[v]
        def chain(e):
            return 1 + chain(seqs[e].seq[0]) if isinstance(e, int) else 0
        for _ in range(10000):
            reach = list(self.reachable())
            worst = None
            for S in reach:
                sq = seqs[S].seq
                for i, e in enumerate(sq):
                    if 1 + chain(e) > D:
                        worst = (S, i); break
                if worst: break
            if not worst:
                return
            P, p = worst
            # walk down the chain; pick the deepest (or, with dcT, the topmost) inline-safe sequence
            cands = []
            while True:
                V = seqs[P].seq[p]
                if not isinstance(V, int): break
                b, c = esc(V)
                if b > 0 and c > 0: cands.append((P, p, V))
                P, p = V, 0
            assert cands, 'no inline-safe sequence on the chain'
            P, p, V = cands[0] if self.DC_TOP else cands[-1]
            old = seqs[P].seq
            new = old[:p] + seqs[V].seq + old[p + 1:]
            seqs[P].seq = new
            self.sequence_lookup[new] = P
            memo_e.clear()
        raise AssertionError('dechain did not converge')

    def build_machine(self):
        self.main()
        self.breakout_common_subsequences()
        for o in self.OPT:
            if o.startswith('dc'):
                self.DC_TOP = o.startswith('dcT')
                self.dechain(int(o[3:] if self.DC_TOP else o[2:]))
        self.reduce_to_cons()
        self.name_sequences()
        self.generate()
        self.tm.gc()
        self.tm.statename = self.tm.start

    def reachable(self):
        # same visiting order as TMBuilder.reachable, with the root index cached (speed only)
        root = getattr(self, '_root', None)
        if root is None or self.sequences[root].name != 'main().0':
            root = self._root = self.find_seq("main().0")
        grey = {root}; black = set(); out = []
        seqs = self.sequences
        while grey:
            i = grey.pop()
            if i not in black:
                out.append(i); black.add(i)
                for v in seqs[i].seq:
                    if isinstance(v, int): grey.add(v)
        return out

    OSEED = None    # randomized tie-breaking in the outliner (None = Wade's deterministic choice)

    def breakout_common_subsequences(self):
        if self.OSEED is None:
            return zf2.ZF2.breakout_common_subsequences(self)
        import random
        rng = random.Random(self.OSEED)
        search_len = max(len(s.seq) for s in self.sequences)
        while search_len > 1:
            reachable = list(self.reachable())
            cnt = {}
            for i in reachable:
                sq = self.sequences[i].seq
                if len(sq) >= search_len:
                    for off in range(len(sq) + 1 - search_len):
                        sub = sq[off:off + search_len]
                        cnt[sub] = cnt.get(sub, 0) + 1
            cands = [k for k, v in cnt.items() if v >= 2]
            if not cands:
                search_len -= 1
                continue
            cands.sort(key=repr)
            match = rng.choice(cands)
            match_i = self.add_sequence(match)
            for i in reachable:
                if i == match_i: continue
                while True:
                    sq = self.sequences[i].seq
                    if len(sq) > search_len:
                        for off in range(len(sq) + 1 - search_len):
                            if sq[off:off + search_len] == match:
                                self.sequences[i].seq = sq[:off] + (match_i,) + sq[off + search_len:]
                                self.sequence_lookup[self.sequences[i].seq] = i
                                break
                        else:
                            break
                    else:
                        break

    def axioms(self):
        return [self.clause(n) for n in self.CLAUSES]

def make(clauses=BASE, perm=None, opt=(), vmap=None, flips=None, oseed=None):
    class V(ZFP):
        pass
    V.OSEED = oseed
    V.CLAUSES = list(clauses); V.PERM = dict(perm or {}); V.OPT = frozenset(opt); V.VMAP = dict(vmap or {}); V.FLIPS = dict(flips or {})
    return V

def build(cls, order):
    z = cls(); z.debug = False; z.AXIOMORDER = list(order); z.build_machine(); return z

def count(z):
    return len(set(s[0] for s in z.tm.states))

def cost(cls, order):
    try: return count(build(cls, order))
    except (AssertionError, RecursionError): return 10**6

CLOSED = {'EXT', 'POW', 'UNI', 'INF', 'PU', 'INF2', 'EXTs'}
import forms as _forms
REPLIKE = _forms.REPLIKE

def valid(clauses, order, opt):
    if clauses[order[-1]] in PREMISE: return False
    if 'b6aD' in opt or 'b6aS' in opt:
        k = [clauses[i] for i in order].index('B6a')
        if any(clauses[i] not in CLOSED for i in order[k + 1:]): return False
    return True
