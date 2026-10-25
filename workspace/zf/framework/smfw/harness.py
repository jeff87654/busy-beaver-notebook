"""SMFW B2 test harness: random tapes -> run a .tm fragment -> decode -> compare to sm_abstract.

Usage:  python -I harness.py [op ...] [--n N] [--seed S]
With no op names, runs all registered ops.
"""
import sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'sm'))
import codec, sim
import sm_abstract as SA

E, EQ, IM, NOT, ALL, V0 = 3, 4, 5, 6, 7, 8

def rwff(rng, depth=3):
    if depth <= 0 or rng.random() < 0.35:
        op = rng.choice([E, EQ])
        return (op, V0 + rng.randrange(4), V0 + rng.randrange(4))
    k = rng.choice([E, EQ, IM, NOT, ALL])
    if k in (E, EQ):
        return (k, V0 + rng.randrange(4), V0 + rng.randrange(4))
    if k == IM:
        return (IM,) + rwff(rng, depth - 1) + rwff(rng, depth - 1)
    if k == NOT:
        return (NOT,) + rwff(rng, depth - 1)
    return (ALL, V0 + rng.randrange(4)) + rwff(rng, depth - 1)

def rvar(rng):
    return (V0 + rng.randrange(5),)

def rstack(rng, lo=1, hi=4):
    return [rwff(rng) for _ in range(rng.randint(lo, hi))]

def rB(rng, want_W=None, maxp=3):
    """Random B: some params (complete wffs/vars) then optionally a last W (theorem, maybe partial)."""
    B = []
    for _ in range(rng.randint(0, maxp)):
        B.append(['param', list(rwff(rng) if rng.random() < 0.7 else rvar(rng))])
    has_W = want_W if want_W is not None else (rng.random() < 0.6)
    if has_W:
        # a (possibly partial) last wff, kind theorem
        w = list(rwff(rng))
        if rng.random() < 0.4:
            w = w[:rng.randint(1, len(w))]      # partial prefix
        B.append(['theorem', w])
    return B

def mk_SM(A, B, c, N=None, rpos=0):
    sm = SA.SM(boot_stack=tuple(A) if A else (SA.BOOT_THEOREM,), check='none')
    sm.A = [tuple(t) for t in A]
    sm.B = [[k, list(v)] for k, v in B]
    sm.c = c
    if N is not None:
        sm.N = list(N); sm.rpos = rpos; sm.placed = list(N[:rpos])
    return sm

def norm(A, B, c):
    return ([tuple(t) for t in A], [[k, list(v)] for k, v in B], c)

ENTRY = {
    'INCC': 'incc.e0', 'DECC': 'decc.e0', 'NEWP': 'newp.e0', 'NEWT': 'newt.e0',
    'APP1': 'app1.e0', 'CHECK': 'check.d0', 'DUPT': 'dupt.e0',
    'PUSH3': 'push.3', 'PUSH4': 'push.4', 'PUSH5': 'push.5', 'PUSH6': 'push.6',
    'PUSH7': 'push.7', 'PUSH8': 'push.8', 'PUSH9': 'push.9', 'PUSH10': 'push.10',
    'PUSH11': 'push.11', 'DUP1': 'dup.1', 'DUP2': 'dup.2', 'DUP3': 'dup.3',
    'DET': 'det.e0', 'COMMIT': 'commit.e0', 'RB': 'rb.e0',
}
TMFILES = ['frag_shared.tm', 'frag_incc.tm', 'frag_decc.tm', 'frag_newpt.tm',
           'frag_app1.tm', 'frag_check.tm', 'frag_push.tm', 'frag_dup.tm',
           'frag_dupt.tm', 'frag_det.tm', 'frag_commit.tm', 'frag_rb.tm']

def load_tbl():
    paths = [os.path.join(HERE, f) for f in TMFILES if os.path.exists(os.path.join(HERE, f))]
    return sim.load(paths)

def run_frag(tbl, op, A, B, c, N=None, rpos=0):
    tape, head = codec.encode(A, B, c, N, rpos)
    out, tape, pos, steps = sim.run(tbl, tape, ENTRY[op], head)
    A2, B2, c2 = codec.decode(tape)
    return out, (A2, B2, c2), tape
