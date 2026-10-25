"""random pre-states for semcheck (2): adapted from zf/reduce/semtest.py's generator (wffs written from Logic.v)."""
from symrm import cpair, add

def weq(x, y): return cpair(cpair(x, y), 0)
def wel(x, y): return cpair(cpair(x, y), 1)
def wim(a, b): return cpair(cpair(a, b), 2)
def wn(a): return cpair(a, 3)
def wal(x, a): return cpair(cpair(x, a), 4)

def rand_wff(rng, depth=0):
    r = rng.random()
    if depth > 3 or r < 0.3: return rng.randrange(0, 6)
    k = rng.randrange(5)
    if k == 0: return weq(rng.randrange(4), rng.randrange(4))
    if k == 1: return wel(rng.randrange(4), rng.randrange(4))
    if k == 2: return wim(rand_wff(rng, depth + 1), rand_wff(rng, depth + 1))
    if k == 3: return wn(rand_wff(rng, depth + 1))
    return wal(rng.randrange(4), rand_wff(rng, depth + 1))

NCL = 20
def random_state(rng):
    """returns ((prooflist, nextproof, topwff, stack-list), info).  The stack list is what main() sees
    BELOW topwff.  With prob 0.4 the list starts with (tw -> ps): main pushes tw, so DET (whenever its
    axiom code is drawn) sees minor = tw, major = tw -> ps and fires; ps = 1 makes the machine halt."""
    ac = rng.choice(list(range(0, NCL + 3)) + list(range(1, NCL + 1)) * 3)
    pv = lambda: rng.choice([rng.randrange(0, 3), rng.randrange(0, 3), rng.randrange(0, 3), rand_wff(rng)])
    p1, p2, p3 = pv(), pv(), pv()
    if rng.random() < 0.1: p1 = 1
    rest = rng.choice([0, 0, rng.randrange(1, 50)])
    tw = rand_wff(rng)
    n = rng.choice([0, 1, 2, 3, 4])
    ws = [rand_wff(rng) for _ in range(n)]
    if rng.random() < 0.4:
        ps = rng.choice([p1, p2, p3])
        ws = [wim(tw, ps)] + ws
    if rng.random() < 0.2 and ws: ws[-1] = 0          # zero entry at the bottom (Cantor: same as absent)
    pl1 = cpair(ac, cpair(p1, cpair(p2, cpair(p3, rest))))
    if rng.random() < 0.15: pl, np = 0, pl1
    else: pl, np = add(pl1, 1), rng.randrange(0, 1000)
    return (pl, np, tw, ws), dict(ac=ac, zpad=rng.choice([0, 0, 1, 3]))
