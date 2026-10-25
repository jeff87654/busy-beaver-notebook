"""PA machine generator: the zfc_254 source (source_local.py) with axioms() replaced by
PA rows + a gated bundle.  Formula ASTs -> RPN tokens -> source_<name>.py -> Wade TMBuilder.

Coding (decoded reading, see DESIGN.md):
    Imp(A,B) = 4P(A,B)        Rel(i,n) = 4P(i,n)+1  : v_i == T(n)
    All(i,A) = 4P(i,A)+2      Eq(i,j)  = 4P(i,j)+3  : v_i == v_j
  term codes T(n), n = 4P(j,k)+t:  t=0: σ v_j (canonical k=j),  t=1: v_j ⊕ v_k,  t=2: v_j ⊗ v_k,
                                   t=3: zero (canonical n=3).
  F = 1 = Rel(0,0) = "v0 == σ v0".

AST:
  formulas  ('rel', x, T) ('eq', x, y) ('im', A, B) ('all', x, A) ('ex', x, A) ('and', A, B)
            ('or', A, B) = ~A -> B   ('not', A)   'phi' (code c)   'u' (literal)   'h' (cache)
  terms     ('S', x)  ('add', x, y)  ('mul', x, y)  'Z'   or a label used as a raw term code
  labels    'a' (param1), 'b' (param2 after read), 'c' (param3), 'd' (= c+1), '0'..'4'
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'ext', 'turing_machine_explorer'))
sys.path.insert(0, HERE)

SRC = os.path.join(HERE, 'source_local.py')

PUSH = {'a': ['par1'], 'b': ['par2'], 'c': ['par3'], 'phi': ['par3'],
        'd': ['par3', 'self.topwff.inc'],
        '0': ['v_0'], '1': ['v_1'], '2': ['v_2'], '3': ['v_3'], '4': ['v_4'],
        'Z': ['v_3'],
        'Z0': ['v_0'],                                       # design A: zero = term code 0
        'u': ['self.pushwff()', 'self.unpair(self.scratch1, self.scratch2, self.prooflist)',
              'self.while_decnz(self.scratch2, self.prooflist.inc)',
              'self.while_decnz(self.scratch1, self.topwff.inc)'],
        'h': ['par2']}           # only valid before the read of param2 (GEN)

SIGMA_CANON = 'jj'               # σ x = wim(x, x)

def rpn(f):
    if isinstance(f, str):
        if f not in PUSH and f.isdigit() and int(f) > 4:      # fixed label n > 4: v_4 then incs
            return ['v_4'] + ['self.topwff.inc'] * (int(f) - 4)
        return list(PUSH[f])
    h = f[0]
    if h == 'rel': return rpn(f[1]) + rpn(f[2]) + ['wel']
    if h == 'eq': return rpn(f[1]) + rpn(f[2]) + ['weq']
    if h == 'im': return rpn(f[1]) + rpn(f[2]) + ['wim']
    if h == 'all': return rpn(f[1]) + rpn(f[2]) + ['wal']
    if h == 'ex': return rpn(f[1]) + rpn(f[2]) + ['wex']
    if h == 'and': return rpn(f[1]) + rpn(f[2]) + ['wa']
    if h == 'not': return rpn(f[1]) + ['wn']
    if h == 'or': return rpn(f[1]) + ['wn'] + rpn(f[2]) + ['wim']
    if h == 'S': return rpn(f[1]) + rpn(f[1]) + ['wim']
    if h == 'add': return rpn(f[1]) + rpn(f[2]) + ['wel']
    if h == 'mul': return rpn(f[1]) + rpn(f[2]) + ['wal']
    if h == 'raw': return list(f[1])
    # ---- design A (functional terms): var / σ(k=1) / zero=code 0 / Eq over terms / σt==u atom
    if h == 'V': return rpn(f[1]) + ['v_0', 'weq']          # Var(i) = 4P(i,0)+3
    if h == 'S1': return rpn(f[1]) + ['v_1', 'wim']         # σt = 4P(t,1)+0
    if h == 'teq': return rpn(f[1]) + rpn(f[2]) + ['weq']   # T(m) == T(n)
    if h == 'srel': return rpn(f[1]) + rpn(f[2]) + ['wel']  # σT(m) == T(n)
    raise ValueError(f)

# ---- helpers
def rel(x, t): return ('rel', x, t)
def eq(x, y): return ('eq', x, y)
def im(*xs):
    return xs[0] if len(xs) == 1 else ('im', xs[0], im(*xs[1:]))
def al(x, a): return ('all', x, a)
def ex(x, a): return ('ex', x, a)
def an(a, b): return ('and', a, b)
def ands(*xs): return xs[0] if len(xs) == 1 else an(xs[0], ands(*xs[1:]))
def no(a): return ('not', a)
def orr(a, b): return ('or', a, b)
def S(x): return ('S', x)
def add(x, y): return ('add', x, y)
def mul(x, y): return ('mul', x, y)
Z = 'Z'
PHI = 'phi'

GATE = ['self.while_decnz(self.param3, [self.scratch1.inc, self.scratch2.inc])',
        'self.if_eq(self.scratch1, self.param2, [self.while_decnz(self.topwff, ())])',
        'self.while_decnz(self.scratch2, self.scratch1.inc)',
        'self.while_decnz(self.param1, self.param2.inc)',
        'self.if_eq(self.scratch1, self.param2, [self.while_decnz(self.topwff, ())])']

LOCALS = """        weq = self.weq()
        wel = self.wel()
        wim = self.wim()
        wn = self.wn()
        wal = self.wal()
        wex = self.wex()
        wa = self.wa()
        v_0 = self.v_0()
        v_1 = self.v_1()
        v_2 = self.v_2()
        v_3 = self.v_3()
        v_4 = self.v_4()
        par1 = self.par1()
        par2 = self.par2()
        par3 = self.par3()
"""

GATE4 = ['self.while_decnz(self.param3, [self.scratch1.inc, self.scratch2.inc])',
         'self.if_eq(self.scratch1, self.param2, [self.while_decnz(self.topwff, ())])',
         'self.while_decnz(self.scratch2, [self.scratch1.inc, self.param2.inc])',
         'self.if_eq(self.scratch1, self.param1, [self.while_decnz(self.topwff, ())])',
         'self.if_eq(self.param2, self.param4, [self.while_decnz(self.topwff, ())])']
REG4 = {'on': False, 'pos': 9}
OCC = {'on': False}       # design option (a): occurs-check gate  c ∉ vars T(a) ∪ vars T(b)

# Occurs-check gate (option a).  Entry: param1 = a, param2 = b, param3 = c, scratch1 = scratch2 = 0,
# topwff = bundle.  Walks the term codes a, b with a work list L (param1) of items x+1 (dual Cantor
# list, 0 = empty).  Item x: 0 = zero (skip); x = 4q+t: t=0 σT(j) (push j), t=1,2 (push j, k),
# t=3 var j (if j = c: topwff := 0).  (j,k) = unP(q).  Exit: all of param1..3, scratch1..2 = 0.
OCC_SRC = """
    @subroutine
    def occ_init(self):
        return [self.param1.inc, self.pair(self.scratch1, self.param1, self.scratch2),
                self.param2.inc, self.pair(self.param1, self.param2, self.scratch1)]

    @subroutine
    def occ_pop(self):
        return [self.unpair(self.param2, self.scratch1, self.param1), self.while_decnz(self.scratch1, self.param1.inc)]

    @subroutine
    def occ_push_j(self):
        return [self.param2.inc, self.pair(self.scratch1, self.param2, self.param1), self.while_decnz(self.scratch1, self.param1.inc)]


    @subroutine
    def occ_jk(self):
        return [self.unpair(self.param2, self.scratch2, self.scratch1)]

    @subroutine
    def occ_h_sigma(self):
        return [self.occ_jk(), self.while_decnz(self.scratch2, ()), self.occ_push_j()]

    @subroutine
    def occ_h_bin(self):
        return [self.occ_jk(), self.occ_push_j(), self.while_decnz(self.scratch2, self.param2.inc), self.occ_push_j1()]

    @subroutine
    def occ_push_j1(self):
        return [self.occ_push_j()]

    @subroutine
    def occ_h_var(self):
        return [self.occ_jk(), self.while_decnz(self.scratch2, ()),
                self.while_decnz(self.param3, [self.scratch1.inc, self.scratch2.inc]),
                self.while_decnz(self.scratch2, self.param3.inc),
                self.if_eq(self.param2, self.scratch1, [self.while_decnz(self.topwff, ())])]

    def occ_dm(self):
        x, q = self.param2, self.scratch1
        s3 = [[x.decnz, [q.inc, 'continue_dm']], [self.occ_h_var(), 'break_dm']]
        s2 = [[x.decnz, s3], [self.occ_h_bin(), 'break_dm']]
        s1 = [[x.decnz, s2], [self.occ_h_bin(), 'break_dm']]
        s0 = [[x.decnz, s1], self.occ_h_sigma()]
        return self.label('dm', s0)

    @subroutine
    def occgate(self):
        x = self.param2
        item = [x.decnz, [x.inc, self.occ_dm()]]          # x = 0 (zero term): skip
        walk = self.label('walk', [self.occ_pop(), [x.decnz, [[item], 'continue_walk']]])
        return [self.occ_init(), walk, self.while_decnz(self.param3, ())]
"""       # design option (b): 4th parameter register d (= u)

def tokens(rows_pre, rows_post, bundle, gate=True):
    if REG4['on']:
        return tokens4(rows_pre, rows_post, bundle)
    if OCC['on']:
        toks = []
        for r in rows_pre: toks += rpn(r)
        toks.append('self.read(self.param2)')
        for r in rows_post: toks += rpn(r)
        toks += rpn(bundle) + ['self.occgate()']
        return toks
    """rows_pre: formulas built before the read of param2 (GEN uses 'h').  rows_post: after.
    'u' must occur exactly once in rows_post.  bundle: the gated current formula (or None)."""
    toks = []
    for r in rows_pre:
        toks += rpn(r)
    toks.append('self.read(self.param2)')
    nu = 0
    for r in rows_post:
        t = rpn(r)
        nu += t.count('self.pushwff()')
        toks += t
    assert nu == 1, 'u must be read exactly once'
    if bundle is not None:
        toks += rpn(bundle)
    if gate:
        toks += GATE
    return toks

def tokens4(rows_pre, rows_post, bundle):
    """u is read into param4 right after param2; 'u' pushes par4 (L's formula u and the free third
    variable of the ternary vacuity rows); the gate also checks c != param4."""
    old = PUSH['u']; PUSH['u'] = ['par4']
    try:
        toks = []
        for r in rows_pre: toks += rpn(r)
        toks += ['self.read(self.param2)', 'self.read(self.param4)']
        for r in rows_post: toks += rpn(r)
        if bundle is not None: toks += rpn(bundle)
        toks += GATE4
    finally:
        PUSH['u'] = old
    return toks

def gen_source(name, toks):
    src = open(SRC, encoding='utf-8').read()
    if REG4['on']:
        regs = ['nextproof', 'topwff', 'wffstack', 'axiomcode', 'param1', 'param2', 'scratch1', 'scratch2', 'prooflist']
        regs.insert(REG4['pos'], 'param4')
        src = src.replace("for name in ['nextproof', 'topwff', 'wffstack', 'axiomcode', 'param1', 'param2', 'scratch1', 'scratch2', 'prooflist']:",
                          "for name in " + repr(regs) + ":")
        p1 = src.index('    @subroutine\n    def par1(self):')
        par4 = ("    @subroutine\n    def par4(self):\n        return [self.pushwff(), self.while_decnz(self.param4, "
                "[self.scratch1.inc, self.topwff.inc]), self.while_decnz(self.scratch1, self.param4.inc)]\n\n")
        src = src[:p1] + par4 + src[p1:]
    if OCC['on']:
        p1 = src.index('    @subroutine' + chr(10) + '    def par1(self):')
        src = src[:p1] + OCC_SRC.lstrip(chr(10)) + chr(10) + src[p1:]
    i = src.index('    def axioms(self):')
    j = src.index('        return [', i)
    k = src.index('\n', j)
    head = '    def axioms(self):\n' + LOCALS + ('        par4 = self.par4()\n' if REG4['on'] else '')
    out = src[:i] + head + '        return [' + ', '.join(toks) + ']' + src[k:]
    path = os.path.join(HERE, f'source_{name}.py')
    open(path, 'w', encoding='utf-8', newline=chr(10)).write(out.replace(chr(13) + chr(10), chr(10)))   # LF only
    return path

def compile_source(name, save=False):
    import importlib
    mod = importlib.import_module(f'source_{name}')
    importlib.reload(mod)
    z = mod.ZF2(); z.debug = False
    z.build_machine()
    if save:
        z.tm.save(os.path.join(HERE, f'pa_{name}.tm'))
    return z, len(set(s[0] for s in z.tm.states))

def build(name, rows_pre, rows_post, bundle, gate=True, save=False, keep=False):
    toks = tokens(rows_pre, rows_post, bundle, gate)
    gen_source(name, toks)
    z, ns = compile_source(name, save)
    if not keep:
        try: os.remove(os.path.join(HERE, f'source_{name}.py'))
        except OSError: pass
    return ns, len(toks)
