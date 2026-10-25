"""Abstract specification of one run of main() of the m254gb source (source_gb.py = zfc_254 with the
AX bundle  (C /\ G') /\ (V-in /\ V=)  extended to  ((C /\ G') /\ (V-in /\ V=)) /\ NG'; everything else as zfc_254).

Persistent state at a command boundary (scratch1 = scratch2 = axiomcode = 0):
    pl  prooflist   remaining command list of the current candidate
    np  nextproof   next candidate number
    tw  topwff      current formula code
    ws  wffstack    theorem stack, P(top, rest); 0 = infinite stream of 0s
    d   param1      additive parameter counter (cleared only by AX)
    h   param2      cached formula (cleared by MP and AX, loaded by NIP)

Coding (dual Cantor pairing P(a,b) = tri(a+b) + b):
    Imp(A,B) = 4P(A,B)   Rel(i,j) = 4P(i,j)+1   All(i,A) = 4P(i,A)+2   Eq(i,j) = 4P(i,j)+3
    Rel(i,j) is v_i e. v_j;  1 = Rel(0,0) = F;  0 = Imp(0,0) ("truth", not the code of any finite wff)
    Not A = Imp(A,1);  A /\\ B = Not(Imp(A, Not B));  E.x A = Not(All(x, Not A)).

enum_step(s) returns the next state, or None if the step halts (NIP with incoming cache 1).
"""

from bignum import P, unP, add, norm   # exact ints below 2^512, fingerprinted values above

def _code(tag, a, b): return add(norm(4 * P(a, b)), tag)
def wim(a, b): return _code(0, a, b)
def wel(i, j): return _code(1, i, j)
def wal(i, a): return _code(2, i, a)
def weq(i, j): return _code(3, i, j)
F = 1
def wn(a): return wim(a, F)
def wa(a, b): return wn(wim(a, wn(b)))
def wex(x, a): return wn(wal(x, wn(a)))

# ---- the AX rows (paper App. A2 names rho1..rho8, in push order rho8 first)
def rho8_L(a, b, c, u):   # ((c -> u) -> a) -> ((a -> c) -> (b -> c))      (Lukasiewicz)
    return wim(wim(wim(c, u), a), wim(wim(a, c), wim(b, c)))
def rho7_eucl(a, b, c):   # c=a -> (c=b -> a=b)
    return wim(weq(c, a), wim(weq(c, b), weq(a, b)))
def rho6_B6c(a, b):       # E.a A.a b -> b
    return wim(wex(a, wal(a, b)), b)
def rho5_cong1(a, b, c):  # c=a -> (c e. b -> a e. b)
    return wim(weq(c, a), wim(wel(c, b), wel(a, b)))
def rho4_comm(a, b, c):   # A.a A.b c -> A.b A.a c
    return wim(wal(a, wal(b, c)), wal(b, wal(a, c)))
def rho3_cong2(a, b, c):  # a=b -> (c e. a -> c e. b)
    return wim(weq(a, b), wim(wel(c, a), wel(c, b)))
def rho2_QI(a, b, c):     # A.a (b -> c) -> (A.a b -> A.a c)
    return wim(wal(a, wim(b, c)), wim(wal(a, b), wal(a, c)))
def rho1_eqex(a, b):      # E.a a=b
    return wex(a, weq(a, b))

# ---- the original zfc_254 bundle (copied from zf/m254/logic/spec.py)
def bundle_C(a, b, c):
    pow_ = wex(c, wa(wal(b, wim(wal(c, wim(wel(c, b), wel(c, a))), wel(b, c))), wel(c, b)))
    tr = wal(c, wim(wel(c, a), wel(c, b)))
    return wex(b, wa(wal(a, wim(wel(a, b), wa(pow_, tr))), wel(c, b)))
def bundle_G(a, b, c):    # c is both the matrix code phi and the output-set variable
    w = wex(b, wa(c, wel(b, c)))
    return wex(c, wa(wal(a, wim(wel(a, b), wal(b, wim(c, w)))), wal(b, wim(wel(b, c), wex(a, c)))))
def bundle_orig(a, b, c):
    vr = wim(wel(a, b), wal(c, wel(a, b)))
    ve = wim(weq(a, b), wal(c, weq(a, b)))
    return wa(wa(bundle_C(a, b, c), bundle_G(a, b, c)), wa(vr, ve))

# ---- NG' (not Goldbach), hand-transcribed from DESIGN.md section 1 (labelled reading), independent
#      of the generator (cands6 / ngdsl).  Labels: n=0, R=1, C=2, F=3 and bound helpers in 0..3.
def _ball(x, s, A): return wal(x, wim(wel(x, s), A))       # A.x (x e. s -> A)
def _bex(x, s, A): return wex(x, wa(wel(x, s), A))         # E.x (x e. s /\ A)
def _or(A, B): return wim(wn(A), B)                        # ~A -> B
def _ng():
    part = wa(_ball(1, 0, _bex(0, 3, wa(wel(1, 0), wal(2, wim(wel(2, 3), wim(wel(1, 2), weq(2, 0))))))),
              _ball(1, 3, _ball(2, 1, wel(2, 0))))                       # Part(n=v0, F=v3)
    nt = _ball(1, 3, _bex(2, 0, wn(wel(2, 1))))                           # NT(n, F)
    allf = wal(3, wim(_or(weq(3, 1), weq(3, 2)), wa(part, nt)))           # F in {R=v1, C=v2}
    g = _ball(0, 1, _ball(1, 2, _bex(2, 0, wa(wel(2, 1), wal(3, wim(wel(3, 0), wim(wel(3, 1), weq(3, 2))))))))
    grid = wa(allf, g)
    comp = wex(1, wex(2, grid))
    two = _bex(0, 3, _bex(1, 3, _ball(2, 3, _or(weq(2, 0), weq(2, 1)))))  # Two(F=v3)
    ev = wex(1, wex(2, wa(grid, wex(3, wa(weq(3, 1), two)))))
    small = wex(3, _ball(2, 0, weq(2, 3)))
    lm = _ball(2, 1, wa(_ball(1, 2, wel(1, 0)),
                        _bex(0, 1, _bex(2, 1, _ball(3, 1, wa(_or(wel(0, 3), weq(0, 3)), wn(wel(2, 3))))))))
    gf = wal(3, wim(wa(part, two), wa(_bex(0, 3, _or(comp, small)), _ball(1, 3, lm))))
    return wex(0, wa(ev, gf))
NG = _ng()

def bundle(a, b, c):
    """m254gb bundle: the zfc_254 bundle /\ NG' (NG' is a closed constant sentence)."""
    return wa(bundle_orig(a, b, c), NG)

def ax_rows(a, h, b, c, u):
    """slots pushed by AX above the old current formula, bottom to top."""
    return [wal(a, h), rho8_L(a, b, c, u), rho7_eucl(a, b, c), rho6_B6c(a, b), rho5_cong1(a, b, c),
            rho4_comm(a, b, c), rho3_cong2(a, b, c), rho2_QI(a, b, c), rho1_eqex(a, b)]

def enum_step(s):
    pl, np, tw, ws, d, h = s
    if pl == 0:
        pl, np = np, np + 1
    else:
        pl -= 1
    ac, pl = unP(pl)
    x, pl = unP(pl)
    d += x
    if ac == 0:                                   # MP
        if wim(tw, d) == h:
            tw, ws = d, P(0, ws)
        else:
            tw = 0
        h = 0
    elif ac == 1:                                 # DROP: push current, current := cache
        tw, ws = h, P(tw, ws)
    elif ac == 2:                                 # NIP: halt on cache F, else cache := pop
        if h == 1:
            return None
        h, ws = unP(ws)
    else:                                         # AX
        c = ac - 3; a = d
        y, pl = unP(pl); b = add(h, y)
        u, pl = unP(pl)
        for r in [tw] + ax_rows(a, h, b, c, u):
            ws = P(r, ws)
        tw = bundle(a, b, c) if (c != a and c != b) else 0
        d = 0; h = 0
    return (pl, np, tw, ws, d, h)
