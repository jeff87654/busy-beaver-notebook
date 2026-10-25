"""SM program (main) as nested lists over SM primitive leaves, compiled with Wade's TMBuilder
machinery (hash-consing, labels, breakout_common_subsequences, reduce_to_cons, name_sequences)
into a decision DAG; exact cell count = number of reachable cons cells (= DAG TM states, the
same count that gives 324 for Wade's zf2.py).

Leaves: RB, DECC (two-outcome: 1/nonzero -> advance, 0/zero -> break 1), PUSH.v, APP1, NEWP,
NEWT, INCC, DUP.k, DUPT, DET, COMMIT, CHECK, plus resolved control leaves _break.k/_continue.k.

Program:
  main      = [ label d: TREE , CHECK ]     (main's end overflows the IP -> restart)
  TREE      = dispatch trie over the 18 axiom codes; internal node = [*pre, [RB, *X], *Y]
              (bit 1 -> X, bit 0 -> Y; 2 cells; pre = longest common body prefix of the group,
              emitted before the bit); every leaf body ends with break_d (-> CHECK)
  body      = [ params..., NEWT, template as PUSH/DUP leaves, COMMIT ]   (DET: [DET];
              GEN: [NEWT, PUSH A, VAR, DUPT, COMMIT])
  READV     = [NEWP, *VAR]           VAR = [PUSH v0, loop v: [RB, APP1, continue v]]
  READW     = [NEWP, loop w: INNER]  typed token reader (see token code below), pending-operand
              counter c' (= pending wffs - 1): '->' INCC, 'e'/'=' DECC (zero branch = done)
     INNER = [PUSH e, E1, VAR, VAR, DECC, continue w]
     E1    = [RB, APP1, RB, APP1, X, INCC, continue w]      (e -> =  -> ->)
     X     = [RB, APP1, Y, continue w]                       (-> -> ~)
     Y     = [RB, APP1, VAR]                                 (~ -> A, then the bound variable)
  wff token code: e=0  ==10  ->=110  ~=1110  A=1111 <var>;  after e/= and A the variables are
  read directly as unary 1^i 0 (typed reader: garbage impossible by construction).
"""
import sys, json, itertools

EXT = r'C:\Users\jeffr\Downloads\bb8\zf\ext\turing_machine_explorer'
if EXT not in sys.path:
    sys.path.insert(0, EXT)
import TMBuilder                       # noqa: E402
from TMBuilder import subroutine       # noqa: E402

E, EQ, IM, NOT, ALL, V0 = 3, 4, 5, 6, 7, 8
TWO_OUTCOME = {'RB', 'DECC'}

# ---------------------------------------------------------------------------- logic
# (name, params, prefix template with macros).  x y z = variable params, p1 p2 p3 = wff params.
# Macros: E x P = ~ A x ~ P ;  /\ P Q = ~ -> P ~ Q ;  <-> P Q = /\ -> P Q -> Q P.
AXIOMS = [
    ('DET', '', None),
    ('GEN', '', None),
    ('B1', 'p1 p2 p3', '-> -> p1 p2 -> -> p2 p3 -> p1 p3'),
    ('B2', 'p1', '-> -> ~ p1 p1 p1'),
    ('B3', 'p1 p2', '-> p1 -> ~ p1 p2'),
    ('B4', 'x p1 p2', '-> A x -> p1 p2 -> A x p1 A x p2'),
    ('B6a', 'x y z', '-> ~ A z = z x -> ~ A z = z y /\\ -> = x y A z = x y -> e x y A z e x y'),
    ('B6b', 'x y p1', '-> A x A y p1 A y A x p1'),
    ('B6c', 'x p1', '-> E x A x p1 p1'),
    ('B7', 'x y', 'E x = x y'),
    ('B8a', 'x y z', '-> = x y -> = x z = y z'),
    ('B8b', 'x y z', '-> = x y -> e x z e y z'),
    ('B8c', 'x y z', '-> = x y -> e z x e z y'),
    ('EXT', '', '-> A v2 <-> e v2 v0 e v2 v1 = v0 v1'),
    ('REP', 'p1', '-> A v3 E v1 A v2 -> A v1 p1 = v2 v1 E v1 A v2 <-> e v2 v1 E v3 /\\ e v3 v0 A v1 p1'),
    ('POW', '', 'E v1 A v2 -> A v3 -> e v3 v2 e v3 v0 e v2 v1'),
    ('UNI', '', 'E v1 A v2 -> E v3 /\\ e v2 v3 e v3 v0 e v2 v1'),
    ('INF', '', 'E v1 /\\ e v0 v1 A v0 -> e v0 v1 E v2 /\\ e v2 v1 A v1 <-> e v1 v2 = v1 v0'),
]
AXNAMES = [a[0] for a in AXIOMS]
AXDICT = {a[0]: a for a in AXIOMS}


def expand(template):
    """Prefix template string -> list of items ('tok', value) | ('par', name), macros expanded."""
    toks = template.split()
    pos = [0]

    def nxt():
        t = toks[pos[0]]
        pos[0] += 1
        return t

    def var():
        t = nxt()
        if t in ('x', 'y', 'z'):
            return [('par', t)]
        assert t[0] == 'v' and t[1:].isdigit(), t
        return [('tok', V0 + int(t[1:]))]

    def wff():
        t = nxt()
        if t in ('p1', 'p2', 'p3'):
            return [('par', t)]
        if t in ('e', '='):
            return [('tok', E if t == 'e' else EQ)] + var() + var()
        if t == '->':
            a = wff(); b = wff()
            return [('tok', IM)] + a + b
        if t == '~':
            return [('tok', NOT)] + wff()
        if t == 'A':
            v = var(); a = wff()
            return [('tok', ALL)] + v + a
        if t == 'E':
            v = var(); a = wff()
            return [('tok', NOT), ('tok', ALL)] + v + [('tok', NOT)] + a
        if t == '/\\':
            a = wff(); b = wff()
            return [('tok', NOT), ('tok', IM)] + a + [('tok', NOT)] + b
        if t == '<->':
            a = wff(); b = wff()
            # /\ -> a b -> b a  =  ~ -> -> a b ~ -> b a
            return [('tok', NOT), ('tok', IM), ('tok', IM)] + a + b + [('tok', NOT), ('tok', IM)] + b + a
        raise ValueError(t)

    out = wff()
    assert pos[0] == len(toks), template
    return out


def instantiate(name, params):
    """Axiom instance as a token tuple; params = dict name -> token tuple (var: 1 token)."""
    _, ps, tpl = AXDICT[name]
    out = []
    for kind, v in expand(tpl):
        out.extend([v] if kind == 'tok' else params[v])
    return tuple(out)


def param_kinds(name):
    return [('V' if p in 'xyz' else 'W') for p in AXDICT[name][1].split()]


# ---------------------------------------------------------------------------- codes
def code_check(code):
    words = [code[a] for a in AXNAMES]
    assert len(set(words)) == len(words)
    for a, b in itertools.permutations(words, 2):
        assert not b.startswith(a), (a, b)
    assert abs(sum(2.0 ** -len(w) for w in words) - 1) < 1e-12, 'prefix code not complete'


def balanced_code(order):
    """Complete prefix code: Huffman-like balanced tree with leaves in the given order."""
    def rec(names, prefix):
        if len(names) == 1:
            return {names[0]: prefix}
        h = len(names) // 2
        d = rec(names[:h], prefix + '1')
        d.update(rec(names[h:], prefix + '0'))
        return d
    return rec(list(order), '')


def comb_code(order):
    """Unary comb: codes 1, 01, 001, ..., 0^(n-1)  (all X-leaves except the last)."""
    n = len(order)
    return {a: ('0' * i + '1' if i < n - 1 else '0' * (n - 1)) for i, a in enumerate(order)}


# Default configuration (prefix code, param reading orders, GEN style) = sm_config.CONFIG, found
# by sm_search.py.  apply_config() installs the param orders into AXDICT (shared with sm_ref).
DEFAULT_CODE = None
DEFAULT_GEN = 'inline'
DEFAULT_FACTOR = True


def apply_config(cfg=None):
    global DEFAULT_CODE, DEFAULT_GEN
    if cfg is None:
        import sm_config
        cfg = sm_config.CONFIG
    base = {a[0]: a for a in AXIOMS}
    for a in AXNAMES:
        AXDICT[a] = base[a]
    for a, o in cfg.get('param_orders', {}).items():
        assert sorted(o.split()) == sorted(base[a][1].split())
        AXDICT[a] = (a, o, base[a][2])
    DEFAULT_CODE = dict(cfg['code'])
    DEFAULT_GEN = cfg.get('gen_style', 'inline')


# ---------------------------------------------------------------------------- bodies / trie
def template_ops(name):
    pnames = AXDICT[name][1].split()
    idx = {p: i + 1 for i, p in enumerate(pnames)}
    return [('PUSH.%d' % v) if k == 'tok' else ('DUP.%d' % idx[v]) for k, v in expand(AXDICT[name][2])]


def body_syms(name, gen_style='inline'):
    """Axiom body as symbols: 'RV' (read variable param), 'RW' (read wff param), 'VAR' (read a
    variable token into W, GEN inline), or a primitive leaf string."""
    if name == 'DET':
        return ['DET']
    if name == 'GEN':
        if gen_style == 'inline':
            return ['NEWT', 'PUSH.%d' % ALL, 'VAR', 'DUPT', 'COMMIT']
        return ['RV', 'NEWT', 'PUSH.%d' % ALL, 'DUP.1', 'DUPT', 'COMMIT']
    return ['RV' if k == 'V' else 'RW' for k in param_kinds(name)] + ['NEWT'] + template_ops(name) + ['COMMIT']


def trie(code, gen_style='inline', factor=True, override=None):
    """Dispatch trie: ('node', pre, X, Y) | ('leaf', name, pre).  At an internal node with axiom
    set S the longest common prefix of S's bodies (beyond what the ancestors emitted) is emitted
    BEFORE the decision bit (factor=True), so shared param reads / NEWT / template prefixes cost
    one cell for the whole group.  X = codes continuing with bit 1, Y = bit 0."""
    override = override or {}
    bodies = {a: list(override.get(a, body_syms(a, gen_style))) for a in code}

    def rec(prefix, done):
        S = [a for a in code if code[a].startswith(prefix)]
        if len(S) == 1:
            return ('leaf', S[0], bodies[S[0]][done:])
        l = done
        if factor:
            while all(len(bodies[a]) > l + 1 for a in S) and len(set(bodies[a][l] for a in S)) == 1:
                l += 1
        pre = bodies[S[0]][done:l]
        return ('node', pre, rec(prefix + '1', l), rec(prefix + '0', l))
    return rec('', 0)


# ---------------------------------------------------------------------------- builder
def _norm(tree):
    """Mimic TMBuilder.add_sequence's list normalisation: drop empty entries, unwrap singletons."""
    while isinstance(tree, (list, tuple)) and len(tree) == 1:
        tree = tree[0]
    if not isinstance(tree, (list, tuple)):
        return tree
    out = tuple(v for v in (_norm(x) for x in tree) if v != ())
    if len(out) == 0:
        return ()
    if len(out) == 1:
        return out[0]
    return out


def leaf_exits(x):
    if x in TWO_OUTCOME:
        return frozenset([('z', 0), ('z', 1)])
    if x.startswith('_break.'):
        return frozenset([('z', int(x.split('.')[1]))])
    if x.startswith('_continue.'):
        return frozenset([('o', int(x.split('.')[1]))])
    if x == 'halt':
        return frozenset()
    assert not x.startswith('break_') and not x.startswith('continue_'), x
    return frozenset([('z', 0)])


class SMBuilder(TMBuilder.TMBuilder):
    def __init__(self, code, gen_style='inline', do_breakout=True, bodies_override=None, factor=True):
        super().__init__()
        self.factor = factor
        code_check(code)
        self.code = code
        self.gen_style = gen_style
        self.do_breakout = do_breakout
        self.bodies_override = bodies_override or {}
        self._exits = {}

    # ---- generalised label (TMBuilder.label only handles 2-element lists along the path)
    def label(self, name, seq, zeros=0, ones=0):
        refs = ('break_' + name, 'continue_' + name)

        def has_ref(t):
            if isinstance(t, str):
                return t in refs
            if isinstance(t, int):
                return name in self.sequences[t].unresolved_labels
            return any(has_ref(x) for x in t)

        def res(t, z, o):
            if isinstance(t, str):
                if t == refs[0]:
                    return '_break.%d' % z
                if t == refs[1]:
                    return '_continue.%d' % o
                return t
            if isinstance(t, int):
                if name in self.sequences[t].unresolved_labels:
                    return res(self.sequences[t].seq, z, o)
                return t
            if not has_ref(t):
                return t
            n = len(t)
            return tuple(res(x, z + 1, o + i) if i < n - 1 else res(x, z, o + i)
                         for i, x in enumerate(t))

        seq = _norm(seq)
        if not has_ref(seq):
            return seq
        assert isinstance(seq, tuple)
        return res(seq, zeros, ones)

    # ---- exits analysis (for safe breakout)
    def exits(self, x):
        if isinstance(x, str):
            return leaf_exits(x)
        if x in self._exits:
            return self._exits[x]
        s = self.sequences[x].seq
        acc = self.exits(s[-1])
        for e in reversed(s[:-1]):
            out = set()
            for k, m in self.exits(e):         # car side
                if k == 'z':
                    if m >= 1:
                        out.add(('z', m - 1))
                else:
                    out.add(('o', m))
            for k, m in acc:                   # cdr side
                if k == 'z':
                    out.add(('z', m))
                elif m >= 2:
                    out.add(('o', m - 1))
            acc = frozenset(out)
        self._exits[x] = acc
        return acc

    def closed(self, x):
        return self.exits(x) <= {('z', 0)}

    def breakout_common_subsequences(self):
        """TMBuilder's algorithm, with (a) the self.reachable bug fixed and (b) only subsequences
        whose elements are all 'closed' (every exit is the normal advance) extracted, so that the
        extraction of a middle subsequence into a car-entered nested sequence cannot change the
        target of a two-outcome zero branch or of a break/continue."""
        if not self.do_breakout:
            return
        search_len = max(len(s.seq) for s in self.sequences)
        while search_len > 1:
            subsequences = set()
            match = None
            reachable = [v for v in self.reachable()]
            for i in reachable:
                s = self.sequences[i]
                if len(s.seq) == search_len:
                    if s.seq in subsequences:
                        match = s.seq
                        break
                    subsequences.add(s.seq)
            if match:
                find = max(i for i in reachable if self.sequences[i].seq == match)
                replace = min(i for i in reachable if self.sequences[i].seq == match)
                self.sequence_lookup[self.sequences[replace].seq] = replace
                for i in reachable:
                    s = self.sequences[i].seq
                    if find in s:
                        self.sequences[i].seq = tuple(v if v != find else replace for v in s)
                        self.sequence_lookup[self.sequences[i].seq] = i
                continue
            for i in reachable:
                s = self.sequences[i]
                if len(s.seq) > search_len:
                    for offset in range(len(s.seq) + 1 - search_len):
                        subseq = s.seq[offset:offset + search_len]
                        if not all(self.closed(x) for x in subseq):
                            continue
                        if subseq in subsequences:
                            match = subseq
                            break
                        subsequences.add(subseq)
                if match:
                    break
            if match:
                match_i = self.add_sequence(match)
                for i in reachable:
                    while True:
                        s = self.sequences[i].seq
                        if len(s) > search_len:
                            for offset in range(len(s) + 1 - search_len):
                                if s[offset:offset + search_len] == match:
                                    self.sequences[i].seq = s[0:offset] + (match_i,) + s[offset + search_len:]
                                    self.sequence_lookup[self.sequences[i].seq] = i
                                    break
                            else:
                                break
                        else:
                            break
            else:
                search_len = search_len - 1

    # ---- program pieces
    @subroutine
    def VAR(self):
        return ['PUSH.%d' % V0, self.label('v', ['RB', 'APP1', 'continue_v'])]

    @subroutine
    def READV(self):
        return ['NEWP', self.VAR()]

    @subroutine
    def READW(self):
        V = self.VAR()
        Y = ['RB', 'APP1', V]
        X = ['RB', 'APP1', Y, 'continue_w']
        E1 = ['RB', 'APP1', 'RB', 'APP1', X, 'INCC', 'continue_w']
        INNER = ['PUSH.%d' % E, E1, V, V, 'DECC', 'continue_w']
        return ['NEWP', self.label('w', INNER)]

    def sym(self, x):
        return {'RV': self.READV, 'RW': self.READW, 'VAR': self.VAR}[x]() if x in ('RV', 'RW', 'VAR') else x

    def tree(self, node=None):
        """Emit the dispatch trie (see trie()): node list = [*pre, [RB, *X], *Y]."""
        if node is None:
            node = trie(self.code, self.gen_style, self.factor, self.bodies_override)
        if node[0] == 'leaf':
            return [self.sym(x) for x in node[2]] + ['break_d']
        _, pre, X, Y = node
        return [self.sym(x) for x in pre] + [['RB'] + self.tree(X)] + self.tree(Y)

    @subroutine
    def main(self):
        return [self.label('d', self.tree()), 'CHECK']

    # ---- build / export
    def build(self):
        self.main()
        self.ids = {}
        for key in ('VAR', 'READV', 'READW'):
            rv = self.memo.get((key,))
            if rv is not None:
                self.ids[key] = self.sequence_lookup[rv] if len(rv) > 1 else None
        self.breakout_common_subsequences()
        self.reduce_to_cons()
        self.name_sequences()
        self.cells = list(self.reachable())
        return len(self.cells)

    @staticmethod
    def leaf_json(x):
        if x.startswith('_break.'):
            return ['break', int(x.split('.')[1])]
        if x.startswith('_continue.'):
            return ['continue', int(x.split('.')[1])]
        if '.' in x:
            op, a = x.split('.')
            return ['op', op, [int(a)]]
        return ['op', x, []]

    def dag(self):
        nodes = {}
        for i in self.cells:
            s = self.sequences[i].seq
            assert len(s) == 2
            nodes[self.sequences[i].name] = [self.sequences[v].name if isinstance(v, int) else self.leaf_json(v)
                                             for v in s]
        return nodes, self.sequences[self.find_seq('main().0')].name


def build(code=None, **kw):
    kw.setdefault('factor', DEFAULT_FACTOR)
    if code is None:
        if DEFAULT_CODE is None:
            apply_config()
        code = DEFAULT_CODE
        kw.setdefault('gen_style', DEFAULT_GEN)
    b = SMBuilder(code, **kw)
    n = b.build()
    return b, n


if __name__ == '__main__':
    pass
