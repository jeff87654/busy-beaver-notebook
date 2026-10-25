"""Abstract string-stack machine (SM) of SM_SPEC.md, plus an interpreter of the decision DAG
with Wade's IP path semantics.

Token values (SM_SPEC section 2):  e=3  ==4  ->=5  ~=6  A=7  v_i=8+i.
Wffs are tuples of token values in prefix (Polish) order.

State (SM_SPEC sections 1-4):
  A   theorem stack: list of token tuples, A[-1] = T_m = top
  B   list of [kind, token list], kind in {'param', 'theorem'}; invariant between ops:
      params first, then at most one theorem-kind W (the wff being built)
  c   the counter c' (the tape run is 1^(c'+3))
  N   candidate bits (list of 0/1), rpos = number already read; placed = bits read so far

Primitives (leaves of the DAG); outcome 'adv' = advance, 'zero' = the decnz-style zero branch
(IP: break 1), 'end' = RB found N exhausted (framework END), 'halt' = CHECK succeeded:
  RB            bit 1 -> adv, bit 0 -> zero, exhausted -> END (B erased, c'=0, IP := [])
  PUSH v        append token v to the last wff of B
  APP1          last token of the last wff of B += 1
  NEWP / NEWT   append an empty param / theorem wff to B
  INCC / DECC   c' += 1 / (c' == 0 ? zero : c' -= 1, adv)
  DUP k         append (a copy of) P_k's tokens to the last wff of B (P_k = k-th entry of B, a param)
  DUPT          append T_m's tokens to the last wff of B
  DET           X = A[-1], Y = A[-2]; X = -> Y ps: pop both, push ps (MATCH);
                X starts with -> but Y mismatches: pop X, keep Y (MISMATCH);
                X does not start with ->: no-op (INVALID); fewer than 2 theorems: no-op.
  COMMIT        drop B's params, the theorem-kind W becomes the new top of A, B := []
  CHECK         halt iff T_m == check_target (default e v0 v0); non-destructive

Resolution of a spec gap (see README): A must never be empty when DUPT runs (GEN on an empty
stack would push the non-wff "A x").  Default boot stack = [BOOT_THEOREM] (an instance of B7);
DET with < 2 theorems is a no-op, so A never becomes empty again.

DAG format (as produced by sm_prog.py, JSON-compatible):
  nodes: name -> [car, cdr]; an entry is either a node name (str) or a leaf list:
     ["op", opname, args]   args = [] or [int]
     ["break", k]           P := inc(strip_zeros(P, k))     (P includes the leaf's own edge bit)
     ["continue", k]        P := strip_ones(P, k)
  path semantics as zf/tools/dag.py RM: node reads bit P[d] (implicit trailing zeros), 0 -> car,
  1 -> cdr; after an 'adv' op P := inc(P); after a 'zero' op P := inc(strip_zeros(P, 1)).
  inc overflow (P = 1^m) restarts main: P := [] (the IP marker moves left; DESIGN.md).
"""

E, EQ, IM, NOT, ALL, V0 = 3, 4, 5, 6, 7, 8
TOKNAME = {3: 'e', 4: '=', 5: '->', 6: '~', 7: 'A'}

# B7 with x = y = v0:  E v0 = v0 v0  =  ~ A v0 ~ = v0 v0
BOOT_THEOREM = (NOT, ALL, V0, NOT, EQ, V0, V0)
CONTRADICTION = (E, V0, V0)


class SMError(Exception):
    pass


def tokstr(t):
    return ' '.join(TOKNAME.get(x, 'v%d' % (x - V0)) for x in t)


def parse_tokens(s):
    """'-> e v0 v1 ~ ...' -> tuple of token values"""
    inv = {v: k for k, v in TOKNAME.items()}
    out = []
    for w in s.split():
        if w in inv:
            out.append(inv[w])
        elif w[0] == 'v' and w[1:].isdigit():
            out.append(V0 + int(w[1:]))
        else:
            raise ValueError(w)
    return tuple(out)


def wff_len(t, i=0):
    """Length of the (unique, prefix-free) wff starting at t[i], or -1 if none."""
    expect = ['W']
    j = i
    n = len(t)
    while expect:
        x = expect.pop()
        if j >= n:
            return -1
        tok = t[j]
        j += 1
        if x == 'V':
            if tok < V0:
                return -1
        elif tok == E or tok == EQ:
            expect.append('V'); expect.append('V')
        elif tok == IM:
            expect.append('W'); expect.append('W')
        elif tok == NOT:
            expect.append('W')
        elif tok == ALL:
            expect.append('W'); expect.append('V')
        else:
            return -1
    return j - i


def prefix_ok(t):
    """True iff t is a prefix of some wff (possibly complete)."""
    expect = ['W']
    for tok in t:
        if not expect:
            return False
        x = expect.pop()
        if x == 'V':
            if tok < V0:
                return False
        elif tok == E or tok == EQ:
            expect.append('V'); expect.append('V')
        elif tok == IM:
            expect.append('W'); expect.append('W')
        elif tok == NOT:
            expect.append('W')
        elif tok == ALL:
            expect.append('W'); expect.append('V')
        else:
            return False
    return True


def is_wff(t):
    return wff_len(t) == len(t) and len(t) > 0


def is_var(t):
    return len(t) == 1 and t[0] >= V0


def inc(P):
    P = list(P)
    i = len(P) - 1
    while i >= 0 and P[i] == 1:
        P[i] = 0
        i -= 1
    if i < 0:
        return []          # overflow: restart main
    P[i] = 1
    return P


def strip(P, bit, k):
    P = list(P)
    while k > 0:
        if not P:
            raise SMError('IP strip underflow')
        if P.pop() == bit:
            k -= 1
    return P


TWO_OUTCOME = {'RB', 'DECC'}


class SM:
    def __init__(self, dag=None, root=None, check_target=CONTRADICTION, boot_stack=(BOOT_THEOREM,),
                 check='incremental'):
        """dag: dict name -> [car, cdr]; check: 'full' (every A/B entry after every op),
        'incremental' (only entries created by the op), or 'none'."""
        self.nodes = dag
        self.root = root
        self.check_target = tuple(check_target)
        self.check = check
        self.A = [tuple(t) for t in boot_stack]
        for t in self.A:
            assert is_wff(t)
        self.B = []
        self.c = 0
        self.N = []
        self.rpos = 0
        self.placed = []
        self.P = []
        self.halted = False
        self.nops = 0
        self.trace = None       # set to a list to record (opname, args, outcome)
        self.visited = None     # set to a set to record the DAG nodes walked through

    # ------------------------------------------------------------------ primitives
    def _last(self):
        if not self.B:
            raise SMError('B empty')
        return self.B[-1][1]

    def prim(self, op, args=()):
        """Execute one primitive; return 'adv' | 'zero' | 'end' | 'halt'."""
        self.nops += 1
        out = 'adv'
        if op == 'RB':
            if self.rpos >= len(self.N):
                # END: framework increments N (outside), erases B, resets c', IP := []
                self.B = []
                self.c = 0
                out = 'end'
            else:
                b = self.N[self.rpos]
                self.rpos += 1
                self.placed.append(b)
                out = 'adv' if b == 1 else 'zero'
        elif op == 'PUSH':
            v = args[0]
            if v < E:
                raise SMError('bad token %d' % v)
            self._last().append(v)
        elif op == 'APP1':
            w = self._last()
            if not w:
                raise SMError('APP1 on empty wff')
            w[-1] += 1
        elif op == 'NEWP':
            self.B.append(['param', []])
        elif op == 'NEWT':
            self.B.append(['theorem', []])
        elif op == 'INCC':
            self.c += 1
        elif op == 'DECC':
            if self.c == 0:
                out = 'zero'
            else:
                self.c -= 1
        elif op == 'DUP':
            k = args[0]
            if not (1 <= k <= len(self.B) - 1) or self.B[k - 1][0] != 'param':
                raise SMError('DUP %d: no such param' % k)
            self._last().extend(self.B[k - 1][1])
        elif op == 'DUPT':
            if not self.A:
                raise SMError('DUPT on empty theorem stack')
            self._last().extend(self.A[-1])
        elif op == 'DET':
            if self.B:
                raise SMError('DET with nonempty B')
            if len(self.A) >= 2:
                X, Y = self.A[-1], self.A[-2]
                if X[0] == IM:
                    if X[1:1 + len(Y)] == Y:
                        ps = X[1 + len(Y):]
                        if not is_wff(ps):
                            raise SMError('DET produced non-wff (prefix-freeness violated?)')
                        self.A.pop(); self.A.pop(); self.A.append(ps)
                        self.last_det = 'match'
                    else:
                        self.A.pop()
                        self.last_det = 'mismatch'
                else:
                    self.last_det = 'invalid'
            else:
                self.last_det = 'underflow'
        elif op == 'COMMIT':
            if not self.B or self.B[-1][0] != 'theorem':
                raise SMError('COMMIT without W')
            for kind, t in self.B[:-1]:
                if kind != 'param':
                    raise SMError('COMMIT: two theorem wffs in B')
                if not (is_wff(t) or is_var(t)):
                    raise SMError('COMMIT: malformed param %r' % (t,))
            W = tuple(self.B[-1][1])
            if self.check != 'none' and not is_wff(W):
                raise SMError('COMMIT of non-wff: ' + tokstr(W))
            self.A.append(W)
            self.B = []
        elif op == 'CHECK':
            if self.A and self.A[-1] == self.check_target:
                self.halted = True
                out = 'halt'
        else:
            raise SMError('unknown op ' + op)
        if self.c < 0:
            raise SMError('negative counter')
        if self.check == 'full':
            self.full_check()
        if self.check in ('full', 'incremental') and op in ('COMMIT', 'DET') and self.A:
            if not is_wff(self.A[-1]):
                raise SMError('non-wff on stack: ' + tokstr(self.A[-1]))
        if self.trace is not None:
            self.trace.append((op, tuple(args), out))
        return out

    def full_check(self):
        # A entries are immutable tuples that only change at the top (COMMIT, DET): checking the
        # top after every op plus every entry at insertion time == checking all after every op.
        if self.A and not is_wff(self.A[-1]):
            raise SMError('non-wff on stack: ' + tokstr(self.A[-1]))
        nth = 0
        for i, (kind, t) in enumerate(self.B):
            if kind == 'theorem':
                nth += 1
                if i != len(self.B) - 1:
                    raise SMError('theorem wff not last in B')
                if not prefix_ok(t):
                    raise SMError('W is not a wff prefix: %r' % (t,))
            elif i != len(self.B) - 1 and not (is_wff(t) or is_var(t)):
                raise SMError('complete param malformed: %r' % (t,))
            elif i == len(self.B) - 1 and not (prefix_ok(t) or (len(t) == 1 and t[0] >= V0)):
                raise SMError('partial last wff is not a wff prefix: %r' % (t,))
        if nth > 1:
            raise SMError('two W in B')

    # ------------------------------------------------------------------ DAG interpreter
    def walk(self):
        cur = self.root
        d = 0
        P = self.P
        nodes = self.nodes
        vis = self.visited
        while isinstance(cur, str):
            if vis is not None:
                vis.add(cur)
            b = P[d] if d < len(P) else 0
            cur = nodes[cur][b]
            d += 1
        if any(P[d:]):
            raise SMError('IP has nonzero bits below a leaf')
        return cur, (P + [0] * d)[:d]

    def step(self):
        """Execute one DAG leaf.  Returns the leaf's outcome ('adv','zero','end','halt','ctl')."""
        leaf, P = self.walk()
        kind = leaf[0]
        if kind == 'op':
            out = self.prim(leaf[1], leaf[2])
            if out == 'adv':
                self.P = inc(P)
            elif out == 'zero':
                self.P = inc(strip(P, 0, 1))
            elif out == 'end':
                self.P = []
            return out
        if kind == 'break':
            self.P = inc(strip(P, 0, leaf[1]))
        elif kind == 'continue':
            self.P = strip(P, 1, leaf[1])
        else:
            raise SMError('bad leaf %r' % (leaf,))
        return 'ctl'

    def run_candidate(self, bits, max_steps=10 ** 7):
        """Run one proof candidate (list of bits, read order) from the current stack.
        Returns 'END' or 'HALT'.  The IP must be at the start of main (P == [])."""
        if self.P != [] or self.B or self.c:
            raise SMError('run_candidate not at main start')
        self.N = list(bits)
        self.rpos = 0
        self.placed = []
        for _ in range(max_steps):
            out = self.step()
            if out == 'halt':
                return 'HALT'
            if out == 'end':
                if self.placed != self.N:
                    raise SMError('N not rotated unchanged')
                return 'END'
        raise SMError('step limit')


def candidate_bits(n):
    """Candidate number n (binary counter of SM_SPEC 5) as read-order bits: LSB first, the last
    bit read is the MSB (always 1 for n > 0); n = 0 is the empty candidate."""
    out = []
    while n:
        out.append(n & 1)
        n >>= 1
    return out


def run_enumeration(dag, root, maxbits, check='incremental', check_target=CONTRADICTION,
                    boot_stack=(BOOT_THEOREM,), stop_n=None, progress=False):
    """Run candidates n = 0 .. 2^maxbits - 1 with the persistent theorem stack.
    Returns (first halting n or None, SM)."""
    sm = SM(dag, root, check_target=check_target, boot_stack=boot_stack, check=check)
    last = (1 << maxbits) if stop_n is None else stop_n + 1
    for n in range(last):
        r = sm.run_candidate(candidate_bits(n))
        if r == 'HALT':
            return n, sm
        if progress and n and (n & (n - 1)) == 0:
            print('  n=%d  |A|=%d ops=%d' % (n, len(sm.A), sm.nops), flush=True)
    return None, sm
