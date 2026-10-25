"""Event simulator with macro clearings and FAKE accumulators (discovery tool, NOT exact).
Standard dynamics in macro form:
  - first digit t>=3: R1-run, t -> t mod 3, A -> 2^n(A+8)-8 (n = t//3); replaced by FAKE[class] when > CAP
  - first digit 1, nearest non-1 token x at position j (positions 1..j-1 are D1):
      x >= 3, A = 1 mod 3: whole consumption of x: x -> x mod 3, positions stay D1, A -> FAKE[1] (deep crossing;
                           exact R2 + R1-run if j == 1 is impossible: j>=2 here)
      x >= 3, A != 1 mod 3: one R2 (x -> x-3, deposit A+3 at j-1, A=4); the deposit is then handled by the rules above
  - anything else: literal simulation (sim.exe) to the next B-form = SPECIAL.
   esim2.py START CAP F0,F1,F2 MAXSPECIALS"""
import sys
from fw import *
from hs import literal_next
from btrace import parse_list


def macro(L, A, cap, fake):
    """one macro move or None if special. returns (tag, L, A)."""
    if not L:
        return None
    t = L[-1]
    if t >= 3:
        n = t // 3
        M = L[:-1] + [t % 3]
        if n > 40:
            A2 = fake[(2 * 0 + A) % 3] if A % 3 == 1 else None
            if A2 is None:   # nonstandard A: 2A+8 alternates 0 <-> 2 mod 3
                A2 = fake[A % 3] if n % 2 == 0 else fake[(2 * A + 8) % 3]
        else:
            A2 = (2 ** n) * (A + 8) - 8
            if A2 > cap:
                A2 = fake[A2 % 3]
        return 'R1x%d' % n, M, A2
    if t == 1:
        j = len(L) - 1
        while j >= 0 and L[j] == 1:
            j -= 1
        if j < 0 or L[j] < 3:
            return None
        if A % 3 == 1 and j <= len(L) - 2:
            M = list(L)
            M[j] = L[j] % 3
            return 'CLR(%d,d%d)' % (L[j], len(L) - 1 - j), M, fake[1]
        M = list(L)
        M[j] -= 3
        M[j + 1] = A + 3
        return 'R2', M, 4
    return None


def esim(L, A, cap, fake, maxspec, log=print, maxmoves=10 ** 7):
    nspec = 0
    tags = []
    for _ in range(maxmoves):
        mv = macro(L, A, cap, fake)
        if mv:
            tag, L, A = mv
            tags.append(tag)
            continue
        kind, L2, A2, st, evs = literal_next(L, A)
        if kind != 'B':
            log('END %s (%d macros) from [%s | %d]: %s' % (kind, len(tags), fmt(L), A, show(L2) if isinstance(L2, dict) else L2))
            return kind, L, A
        log('SPECIAL (%s) [%s | %d] -> [%s | %d]  %d st, %d E0' % (
            ' '.join(tags[:6]) + (' ...%d' % len(tags) if len(tags) > 6 else ''), fmt(L), A, fmt(L2), A2, st, len(evs)))
        tags = []
        L, A = L2, A2
        nspec += 1
        if nspec >= maxspec:
            return 'MAXSPEC', L, A
    return 'MAXMOVES', L, A


if __name__ == '__main__':
    _, ts, A = sys.argv[1].split(':')
    cap = int(sys.argv[2]); fake = [int(x) for x in sys.argv[3].split(',')]
    esim(parse_list(ts), int(A), cap, fake, int(sys.argv[4]), log=lambda s: print(s, flush=True))
