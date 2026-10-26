"""Abstract M13-family model, extended with a third outer counter e (route to f_(w+3)).

M13 semantics (BB13_M13.v):
    Ce(p,a,c,d):  while c>0   -> Kc step             (each Kc step ~ f_w)
                  c==0, d>=2  -> Kd_step             (~ f_(w+1); halves a into c=a/2+1)
                  c==0, d==0  -> D_reload; d := a+1  (~ f_(w+2) once; d is accumulator-sized)
                  c==0, d==1  -> HALT

    Kc(p,a)       = (p + a/2, W(p-1)(1))
    Kd_step(p,a)  = iter(a/2+1) Kc (p-1, 2)
    D_reload(p,a) = Kc(p-2, 2)
    W_0(b)=b+3,   W_(j+1)(b) = W_j^(b+1)(2)

f_(w+3) extension (the D_REL gadget that search_w3b looks for):
    c==0, d==0        -> D_reload; d := a+1; if e is absent then e := a+1   (create e)
    c==0, d==1, e==1  -> HALT
    c==0, d==1, e>=2  -> e -= 1; D_reload; d := a+1                        (one more w+2 round)

i.e. the number of w+2 rounds becomes the counter e instead of a hard-wired constant.
"""
import sys

sys.setrecursionlimit(100000)

CAP = 10 ** 6
KC = 0
ROUNDS = 0


class Big(Exception):
    pass


def _chk(x):
    if CAP is not None and x > CAP:
        raise Big()
    return x


def W_rec(j, b):
    if j == 0:
        return _chk(b + 3)
    cur = 2
    for _ in range(b + 1):
        cur = _chk(W_rec(j - 1, cur))
    return cur


def Kc(p, a):
    global KC
    KC += 1
    return (p + a // 2, W_rec(p - 1, 1))


def Kc_iter(n, p, a):
    for _ in range(n):
        p, a = Kc(p, a)
    return p, a


def Kd_step(p, a):
    return Kc_iter(a // 2 + 1, p - 1, 2)


def D_reload(p, a):
    return Kc(p - 2, 2)


def run(p, a, c, d, e, max_rounds=10 ** 5):
    """Return (kind, kc_steps, p, a, c, d, e)."""
    global KC, ROUNDS
    KC = 0
    ROUNDS = 0
    rounds = 0
    while True:
        while c > 0:
            p, a = Kc(p, a)
            c -= 1
        if d >= 2:
            p, a = Kd_step(p, a)
            d -= 1
            rounds += 1
        elif d == 1:
            if e == 1:
                return ('HALT', KC, p, a, c, d, e)
            if e is None:
                return ('HALT(no-e)', KC, p, a, c, d, e)
            e -= 1
            p, a = D_reload(p, a)
            d = a + 1
            rounds += 1
        else:  # d == 0
            p, a = D_reload(p, a)
            if e is None:
                e = a + 1
            d = a + 1
            rounds += 1
        if rounds > max_rounds:
            return ('BIG', KC, p, a, c, d, e)
        ROUNDS = rounds


def guarded(tag, fn):
    global CAP
    try:
        print(f"  {tag} -> {fn()}")
    except Big:
        print(f"  {tag} -> BIG (> {CAP}) after {ROUNDS} rounds, {KC} Kc steps")


def main():
    global CAP, KC, ROUNDS
    CAP = 10 ** 4
    print("Reference (M13/M14 family, no e counter):")
    guarded("Ce(1,2,0,1)", lambda: run(1, 2, 0, 1, None))
    guarded("Ce(1,2,2,1)  (M13-like, one w+2 round)", lambda: run(1, 2, 2, 1, None))

    print("\nf_(w+3) variant: D_REL at d==1 decrements e; halt only at e==1.")
    print("Start Ce(1,2,2,1); each e-step buys one more accumulator-sized d-run:")
    for E in (1, 2, 3, 4, 5, 6):
        guarded(f"e={E}", lambda E=E: run(1, 2, 2, 1, E, max_rounds=6))

    print("\nThe numeric size saturates the cap inside the first round for every e >= 2")
    print("(one round is already a tower), so the cap cannot resolve e numerically.")
    print("What e controls is structural and exact: e=k performs exactly k")
    print("accumulator-sized d-runs (k f_(w+2) stages) and then halts.")
    print("A concrete machine must therefore supply the three d==1/e branches:")
    print("  e absent at the first refill -> create e = Theta(accumulator)")
    print("  e >= 2                       -> e -= 1 and one more D_reload")
    print("  e == 1                       -> halt")


if __name__ == '__main__':
    main()
