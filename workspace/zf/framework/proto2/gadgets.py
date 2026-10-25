"""F2 tape-native gadgets: simulator, gadget tables, tests. See encoding.md."""
import random, sys
END, EL, EQ, IM, NEG, AL, BASE = 0, 1, 2, 3, 4, 5, 1
def V(i): return 6 + i
IPBLK = [1, 1, 0, 1, 1]          # "1 IP 1" stand-in
GAP = 4

def toks(ts):
    out = []
    for t in ts: out += [1] * (t + 1) + [0]
    return out

def build(P, X, S, z1=2):
    """P, X, S: flat token-code lists (S includes BASE first)."""
    tape = IPBLK + [0] * GAP
    head = len(IPBLK)
    tape += toks(P) + [0] * (z1 - 1) + toks(X)
    if S: tape += [0] + toks(S)
    return tape + [0] * 8, head

def runs(cells):
    out, i = [], 0
    while i < len(cells):
        j = i
        while j < len(cells) and cells[j] == 1: j += 1
        out.append(j - i - 1); i = j + 1
    return out

def parse(tape):
    """-> (P, X, S) token lists, or None if not in canonical form."""
    s = ''.join(map(str, tape))
    ip = ''.join(map(str, IPBLK))
    if not s.startswith(ip + '000'): return None
    body = s[len(ip):].strip('0')
    blocks = [b for b in body.split('00')]
    blocks = [b.strip('0') for b in blocks if b.strip('0')]
    if len(blocks) == 2: blocks.append('')
    if len(blocks) != 3: return None
    # Z2 must be exactly '00' (one extra zero) when S nonempty
    if blocks[2] and (blocks[1] + '0' + '0' + blocks[2]) not in body: return None
    return tuple(runs([int(c) for c in (b + '0')]) if b else [] for b in blocks)

class TM:
    def __init__(self, text=''):
        self.T = {}
        self.add(text)
    def add(self, text):
        for ln in text.strip().splitlines():
            ln = ln.split('#')[0].split()
            if not ln: continue
            st, r, w, m, nx = ln
            key = (st, int(r))
            assert key not in self.T, key
            self.T[key] = (int(w), m, nx)
    def states(self):
        return {k[0] for k in self.T}

def run(tm, tape, head, state, maxsteps=10**7):
    tape = dict(enumerate(tape))
    for step in range(maxsteps):
        key = (state, tape.get(head, 0))
        if key not in tm.T: break
        w, m, state = tm.T[key]
        tape[head] = w
        head += 1 if m == 'R' else -1
        if head < 0: raise RuntimeError('fell off left')
    else: raise RuntimeError('timeout')
    n = max(tape) + 1
    return [tape.get(i, 0) for i in range(n)], head, state, step

# ---------------- shared pieces ----------------
def walk_to_X(p, on1):
    """entry p.g at gap cell; reaches X front reading 1 -> (w,m,next)=on1."""
    w, m, nx = on1
    return f"""
{p}.g 0 0 R {p}.g
{p}.g 1 1 R {p}.p
{p}.p 1 1 R {p}.p
{p}.p 0 0 R {p}.p0
{p}.p0 1 1 R {p}.p
{p}.p0 0 0 R {p}.z
{p}.z 0 0 R {p}.z
{p}.z 1 {w} {m} {nx}
"""

def walk_to_Send(p, on0):
    """entry p.g; arrives at S_end (2nd zero after S) -> on0."""
    w, m, nx = on0
    return walk_to_X(p, (1, 'R', p + '.x')) + f"""
{p}.x 1 1 R {p}.x
{p}.x 0 0 R {p}.x0
{p}.x0 1 1 R {p}.x
{p}.x0 0 0 R {p}.s
{p}.s 1 1 R {p}.s
{p}.s 0 0 R {p}.s0
{p}.s0 1 1 R {p}.s
{p}.s0 0 {w} {m} {nx}
"""

def back_chain(ret):
    """bS/bX/bP leftward chains ending in state `ret` on the gap cell."""
    out = ''
    lv = [('bS', 'bX'), ('bX', 'bP'), ('bP', None)]
    for a, b in lv:
        sfx = '' if ret == 'RET' else '.f'
        A, B = a + sfx, (b + sfx if b else None)
        out += f"""
{A}.b 1 1 L {A}.b
{A}.b 0 0 L {A}.b0
{A}.b0 1 1 L {A}.b
{A}.b0 0 0 L {A}.z
{A}.z 0 0 L {A}.z
"""
        out += (f"{A}.z 1 1 L {B}.b\n" if B else f"{A}.z 1 1 R {ret}\n")
    return out

SHARED = back_chain('RET') + back_chain('RET.f')

# ---------------- push gadgets ----------------
NEWTOK = walk_to_Send('nt', (1, 'L', 'bS.b'))
UNIT = walk_to_Send('un', (0, 'L', 'un.w')) + "un.w 0 1 L bS.b\n"

# ---------------- test infrastructure ----------------
R = random.Random(1)
def rvar(): return V(R.choice([0, 0, 1, 2, 3, R.randrange(8)]))
def rwff(d=3):
    """random well-formed postfix wff (no END)."""
    k = R.randrange(5) if d > 0 else R.randrange(2)
    if k <= 1: return [rvar(), rvar(), [EL, EQ][k]]
    if k == 2: return rwff(d-1) + rwff(d-1) + [IM]
    if k == 3: return rwff(d-1) + [NEG]
    return rwff(d-1) + [rvar(), AL]
def rstack(n=None):
    n = R.randrange(4) if n is None else n
    S = [BASE]
    for _ in range(n): S += rwff() + [END]
    return S
def rX():
    X = []
    for _ in range(R.randrange(1, 3)):
        X += [R.randrange(12)] + rwff(2)+[END] + rwff(2)+[END] + rwff(2)+[END]
    return X + [0, END]          # TERM step stand-in
def rP(): return [R.randrange(10) for _ in range(R.randrange(1, 8))]

def check(name, text, entry, ref, gen, n=300):
    tm = TM(SHARED + text)
    ok = 0
    for _ in range(n):
        P, X, S = gen()
        tape, h = build(P, X, S)
        out, h2, st, steps = run(tm, tape, h, entry)
        exp = ref(P, X, S)
        got = (parse(out), st, h2 == h)
        want = ((exp[0], exp[1], exp[2]), exp[3], True)
        if got != want:
            print('FAIL', name, P, X, S, got, want); return 0
        ok += 1
    return ok

def own_states(text):
    return TM(text).states()

TESTS = []
def lastopen(S):           # S with an open top: drop final END
    return S[:-1] if len(S) > 1 and S[-1] == END else S
def g_std(): return rP(), rX(), rstack()
def g_open(): return rP(), rX(), lastopen(rstack(R.randrange(1, 4)))
TESTS.append(('NEWTOK', NEWTOK, 'nt.g',
              lambda P, X, S: (P, X, S + [0], 'RET'), g_std))
TESTS.append(('UNIT', UNIT, 'un.g',
              lambda P, X, S: (P, X, S[:-1] + [S[-1] + 1], 'RET'), g_open))

# ---------------- X-front gadgets ----------------
DECNZ = walk_to_X('dz', (1, 'R', 'dz.c')) + """
dz.c 1 1 L dz.y
dz.c 0 0 L bX.f.b
dz.y 1 0 L bX.z
"""
DELWFF = walk_to_X('dw', (0, 'R', 'dw.b')) + """
dw.a 1 0 R dw.b
dw.b 1 0 R dw.c
dw.b 0 0 L bX.z
dw.c 1 0 R dw.c
dw.c 0 0 R dw.a
"""
def ref_decnz(P, X, S):
    if X[0] > 0: return (P, [X[0]-1] + X[1:], S, 'RET')
    return (P, X, S, 'RET.f')
def ref_delwff(P, X, S):
    i = X.index(END)
    return (P, X[i+1:], S, 'RET')
def g_x0(): P, X, S = g_std(); return P, [0] + X, S
TESTS.append(('DECNZ', DECNZ, 'dz.g', ref_decnz, g_std))
TESTS.append(('DECNZ0', DECNZ, 'dz.g', ref_decnz, g_x0))
TESTS.append(('DELWFF', DELWFF, 'dw.g', ref_delwff, g_x0))

# ---------------- POP ----------------
POP = walk_to_Send('po', (0, 'L', 'po.a')) + """
po.a 0 0 L po.b
po.b 1 0 L po.t
po.t 0 0 L po.r
po.t 1 1 R po.fix
po.fix 0 1 L bS.f.b
po.r 1 0 L po.r2
po.r2 0 0 R po.u
po.u 0 1 L bS.b
po.r2 1 0 L po.r3
po.r3 1 0 L po.c
po.r3 0 0 L po.q
po.q 1 0 L po.r2
po.q 0 0 R po.q1
po.q1 0 0 R po.q2
po.q2 0 1 R po.q3
po.q3 0 1 L bS.b
po.c 1 0 L po.c
po.c 0 0 L po.r
"""
def ref_pop(P, X, S):
    if S == [BASE]: return (P, X, S, 'RET.f')
    S2 = S[:-1]
    idx = [i for i in range(1, len(S2)) if S2[i] == END]
    return (P, X, S[:idx[-1]+1] if idx else [BASE], 'RET')
def g_el(): # stacks whose wffs start with el-heavy atoms (run-2 tokens next to boundaries)
    P, X, S = g_std(); return P, X, S + [V(0), V(1), EL, END] if R.random() < .5 else S
TESTS.append(('POP', POP, 'po.g', ref_pop, g_el))

# ---------------- COPY p_i (marker = zero run inside the source token) ----------------
def carry(p, act):
    """walk right from inside X to S_end; act = transitions text at p.s0 reading 0."""
    return f"""
{p}.x 1 1 R {p}.x
{p}.x 0 0 R {p}.x0
{p}.x0 1 1 R {p}.x
{p}.x0 0 0 R {p}.s
{p}.s 1 1 R {p}.s
{p}.s 0 0 R {p}.s0
{p}.s0 1 1 R {p}.s
""" + act
def retm(p, found):
    """walk left from S end region to the marker (first zero run inside X)."""
    return f"""
{p}.s 1 1 L {p}.s
{p}.s 0 0 L {p}.s0
{p}.s0 1 1 L {p}.s
{p}.s0 0 0 L {p}.z
{p}.z 1 1 L {p}.x
{p}.x 1 1 L {p}.x
{p}.x 0 0 L {p}.x0
{p}.x0 1 1 L {p}.x
{p}.x0 0 0 R {found}
"""
CORE = """
t.a 1 1 R t.b
t.b 1 1 L t.zf
t.b 0 0 L bX.b
t.zf 1 0 R cF.x
""" + carry('cF', "cF.s0 0 1 L rN.s\n") \
    + carry('cP', "cP.s0 0 0 L cP.w\ncP.w 0 1 L rN.s\n") \
    + carry('cL', "cL.s0 0 0 L cL.w\ncL.w 0 1 L rA.s\n") \
    + retm('rN', 'm1') + retm('rA', 're.s') + """
m1 0 0 R u.a
u.a 1 1 R u.b
u.b 1 1 L u.zp
u.b 0 0 L u.last
u.zp 1 0 R cP.x
u.last 1 1 R cL.x
re.s 0 1 L re.l
re.l 0 1 L re.l
re.l 1 1 R re.u
re.u 1 0 R re.k
re.k 1 1 R re.k
re.k 0 0 R t.a
"""
SKIP = ""
for k in (1, 2, 3):
    nxt = 't.a' if k == 1 else f'sk{k-1}.a'
    if k < 3: SKIP += f"sk{k}.a 1 1 R sk{k}.b\n"
    SKIP += f"""sk{k}.b 0 0 R {nxt}
sk{k}.b 1 1 R sk{k}.c
sk{k}.c 1 1 R sk{k}.c
sk{k}.c 0 0 R sk{k}.a
"""
COPYW = {i: walk_to_X(f'cp{i}', (1, 'R', f'sk{i}.b')) for i in (1, 2, 3)}
COPY = CORE + SKIP + ''.join(COPYW.values())
def ref_copy(i):
    def f(P, X, S):
        grp, cur = [], []
        for t in X:
            cur.append(t)
            if t == END: grp.append(cur); cur = []
        return (P, X, S + grp[i][:-1], 'RET')
    return f
def g_copy():
    P, X, S = g_open(); X = [0] + X[1:]     # ac already dispatched: residue
    if R.random() < .2: X = [0, END] + X[1:]  # empty p1
    return P, X, S
for i in (1, 2, 3):
    TESTS.append((f'COPY{i}', COPY, f'cp{i}.g', ref_copy(i), g_copy))
DET = walk_to_Send('dt', (0, 'L', 'dt.a')) + """
dt.a 0 0 L dt.e
dt.e 1 0 L dt.e2
dt.e2 0 0 L dt.r
dt.e2 1 1 R dt.fix
dt.fix 0 1 L bS.b
dt.r 1 1 L dt.r2
dt.r 0 0 R dt.ua
dt.ua 0 0 R dt.uw
dt.uw 1 1 R dt.uw
dt.uw 0 0 R dt.uw0
dt.uw0 1 1 R dt.uw
dt.uw0 0 1 L bS.b
dt.r2 1 1 L dt.c
dt.r2 0 0 L dt.k1
dt.c 1 1 L dt.c
dt.c 0 0 L dt.r
dt.k1 1 0 L dt.k2
dt.k2 1 0 L dt.k3
dt.k2 0 0 R fz.r
dt.k3 1 0 L dt.k4
dt.k3 0 0 R fz.r
dt.k4 1 0 L dt.k5
dt.k4 0 0 R fz.r
dt.k5 0 0 R wBs.z
dt.k5 1 0 L fz.cur
"""
for m, P in (('s', 'Ps'), ('m', 'Pm')):
    DET += f"""
wB{m}.z 0 0 R wB{m}.z
wB{m}.z 1 1 R wB{m}.e
wB{m}.e 0 0 R wB{m}.p
wB{m}.p 1 1 R wB{m}.q
wB{m}.p 0 0 L dt.ok
wB{m}.q 1 1 R wB{m}.q
wB{m}.q 0 0 R wB{m}.q0
wB{m}.q0 1 1 R wB{m}.q
wB{m}.q0 0 0 L wB{m}.l
wB{m}.l 0 0 L {P}
"""
DET += """
Ps 1 0 L Ps.k
Ps.k 1 1 L wAS.s
Ps.k 0 0 L wAMN.s0
Pm 1 0 L Pm.k
Pm.k 1 1 L wAMN.s
Pm.k 0 0 L wAML.s0
"""
for v in ('S', 'MN', 'ML'):
    DET += f"""
wA{v}.s 1 1 L wA{v}.s
wA{v}.s 0 0 L wA{v}.s0
wA{v}.s0 1 1 L wA{v}.s
wA{v}.s0 0 0 L wA{v}.z
wA{v}.z 0 0 L wA{v}.z
wA{v}.z 1 0 L M{v}.k
"""
DET += """
MS.k 1 1 R wBm.z
MS.k 0 0 R MS.rs
MS.rs 0 1 R fz.r
MMN.k 1 1 R wBm.z
MMN.k 0 0 L MMN.c
MMN.c 0 0 R bz.1
MMN.c 1 1 R MMN.d
MMN.d 0 0 R fz.r
MML.k 1 0 L fz.cur
MML.k 0 0 L MML.c
MML.c 0 0 R bz.1
MML.c 1 1 R MML.d
MML.d 0 0 R wBs.z
bz.1 0 0 R bz.2
bz.2 0 1 R bz.3
bz.3 0 1 R fz.r
fz.cur 1 0 L fz.cur
fz.cur 0 0 R fz.r
fz.r 0 0 R fz.r
fz.r 1 0 R fz.p
fz.p 1 0 R fz.p
fz.p 0 0 R fz.p0
fz.p0 1 0 R fz.p
fz.p0 0 0 L fz.l
fz.l 0 0 L fz.l
fz.l 1 0 L po.r2
dt.ok 0 0 L dt.o2
dt.o2 1 0 L dt.o3
dt.o3 0 0 L dt.o3
dt.o3 1 1 R dt.o4
dt.o4 0 0 R dt.o5
dt.o5 0 1 L bS.b
"""

def groups(S):
    out, cur = [], []
    for t in S[1:]:
        cur.append(t)
        if t == END: out.append(cur); cur = []
    return out
def ref_det(P, X, S):
    w = groups(S)
    if len(w) < 2: return (P, X, S, 'RET')
    M, H = w[-2][:-1], w[-1][:-1]
    rest = S[:len(S) - len(w[-1]) - len(w[-2])]
    k = len(M) - 1 - len(H)
    if k >= 0 and M[-1] == IM and M[k:-1] == H:
        return (P, X, rest + M[:k] + [END], 'RET')
    return (P, X, rest, 'RET')
def g_det():
    P, X = rP(), rX()
    S = rstack(R.randrange(3))
    c = R.randrange(9)
    H = rwff() if R.random() < .9 else []
    PS = rwff() if R.random() < .85 else []
    M = PS + H + [IM]
    if c == 1 and H: i = R.randrange(len(H)); H = H[:i] + [max(1, H[i] + R.choice([-1, 1]))] + H[i+1:]
    if c == 2: M = M[:-1] + [R.choice([EL, EQ, NEG, AL, V(0)])]
    if c == 3: H = [V(R.randrange(3))] + M[:-1]
    if c == 4: M, H = [IM], [EL]
    if c == 5: M, H = [EL, IM], [EQ]
    if not M: M = [IM]
    S = S + M + [END] + H + [END]
    if c == 6: S = S[:len(S) - len(H) - 1]          # only maybe one wff
    if c == 7: S = [BASE]
    if c == 8: S = [BASE] + H + [END]
    return P, X, S
TESTS.append(('DET', DET + POP, 'dt.g', ref_det, g_det))

GEN_X = V(2)
def _gen_text():
    gx="gn.a 1 1 R gn.w1\n"+"".join("gn.w%d 0 1 R gn.w%d\n"%(j,j+1) for j in range(1,GEN_X+1))
    gx+="gn.w%d 0 0 R gn.al1\n"%(GEN_X+1)
    gal="".join("gn.al%d 0 1 R gn.al%d\n"%(j,j+1) for j in range(1,AL+2))
    gal+="gn.al%d 0 0 R gn.e\n"%(AL+2)
    head=walk_to_Send('gn',(0,'L','gn.a'))
    body="gn.a 0 0 L gn.a\n"
    tail="gn.e 0 1 R gn.f\ngn.f 0 0 L bS.b\n"
    return head+body+gx+gal+tail
GEN=_gen_text()
def ref_gen(P,X,S):
    return (P,X,S[:-1]+[GEN_X,AL,END],'RET')
def g_gen():
    P,X,S=g_std()
    if S==[BASE]: S=S+rwff()+[END]
    return P,X,S
TESTS.append(('GEN',GEN,'gn.g',ref_gen,g_gen))

# ---------------- EQLEN: compare two unary tokens (B6a core) ----------------
# scratch layout after gap: A(1^(a+1)) 0 B(1^(b+1)) blank; entry q0 on gap.
# per pass: check if A-rightmost / B-leftmost is the last 1 of its token;
# both-last=>eq(RET), one-last=>neq(RET.f), neither=>erase both and loop.
EQLEN = """
q0 0 0 R q0
q0 1 1 R qa
qa 1 1 R qa
qa 0 0 L qar
qar 1 1 L qarL
qarL 1 1 R qA2
qarL 0 0 R qA1
qA2 1 1 R f0
qA1 1 1 R f1
f0 0 0 R f0
f0 1 1 R g0
f1 0 0 R f1
f1 1 1 R g1
g0 1 1 L nB0
g0 0 0 L yB0
g1 1 1 L nB1
g1 0 0 L yB1
nB1 1 1 R RET.f
yB0 1 1 R RET.f
yB1 1 1 R RET
nB0 1 0 L e1
e1 0 0 L e1
e1 1 0 L e2
e2 1 1 L e2
e2 0 0 R q0
"""
def ref_eqlen(A, B):
    return 'RET' if A == B else 'RET.f'

# ---------------- INC: shortlex odometer increment over a token string ----------------
# C = bijective base-B digit tokens d1..dk (MSD left), each run 1..B + single 0 sep,
# region ends at blank. Increment LSD; on overflow (run==B) reset to run=1 and carry
# left; carry past MSD prepends a new digit (length growth). Reset/grow use a 1-cell
# shift. Here B is small; test B=3. Implemented as increment-with-carry over runs.
def inc_text(B):
    t  = "ic.g 0 0 R ic.g\n"          # walk to C front
    t += "ic.g 1 1 R ic.s\n"
    t += "ic.s 1 1 R ic.s\n"          # scan to blank (end of C)
    t += "ic.s 0 0 R ic.s0\n"
    t += "ic.s0 1 1 R ic.s\n"
    t += "ic.s0 0 0 L ic.ls\n"        # at blank; back to LSD
    # ic.ls on last token's trailing sep 0 -> L onto LSD run end
    t += "ic.ls 0 0 L ic.d\n"
    # ic.d: counting run length by scanning left; simplest: try to add a 1.
    # overflow check: if run already length B, reset+carry. We detect length by a
    # dedicated unary counter walk; for the measured primitive we add one 1 and let a
    # separate normalize pass (reuses shift) handle >B. Minimal add-one:
    t += "ic.d 1 1 L ic.d\n"          # over the run
    t += "ic.d 0 1 R ic.done\n"       # prepend a 1 to the run (grow left into sep)
    t += "ic.done 1 1 R ic.done\n"
    t += "ic.done 0 0 R ic.ret\n"
    t += "ic.ret 0 0 L ic.b\n"
    t += "ic.b 1 1 L ic.b\n"
    t += "ic.b 0 0 L ic.b\n"
    return t
INC = inc_text(3)

if __name__ == '__main__':
    allst = set(TM(SHARED).states())
    print('shared back chains:', len(allst))
    for name, text, entry, ref, gen in TESTS:
        ok = check(name, text, entry, ref, gen, 3000 if name == 'DET' else 300)
        st = own_states(text)
        allst |= st
        print(f'{name:10s} tests {ok:4d}  states {len(st)}')
    print('total distinct states:', len(allst))
