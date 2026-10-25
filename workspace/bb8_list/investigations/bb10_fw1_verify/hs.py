"""Hybrid simulator on B-form configurations [L | A] (tape D(L0)..D(Ln-1) D0 D(A) G>).
Standard moves done in Python (R1: first digit t>=3; R2: borrow through D1's from a token t>=3); everything else
('special') by literal simulation (sim.exe) to the next B-form configuration.  check=True runs EVERY move literally
and compares (rule validation)."""
import sys
from fw import *


def std_move(L, A):
    if L and L[-1] >= 3:
        return 'R1', L[:-1] + [L[-1] - 3], 2 * A + 8
    if L and L[-1] == 1:
        j = len(L) - 1
        while j >= 0 and L[j] == 1:
            j -= 1
        if j >= 0 and L[j] >= 3:
            M = list(L)
            M[j] -= 3
            M[j + 1] = A + 3
            return 'R2', M, 4
    return None


_SRV = None


def literal_next(L, A, maxsteps=10 ** 10, events='Bf,E0'):
    """run from B-form [L|A] to the next B-form; returns (kind, L', A', steps, extra_events) ."""
    global _SRV
    if _SRV is None:
        _SRV = Server(M10, 'Bf,E0')
    w, h, q = bword(L, A)
    evs = []
    for x in _SRV.job(w, h, q, maxsteps):
        if x['kind'] == 'BF':
            p = bparse(x['word'], x['rel'])
            assert p is not None, 'BF parse failed'
            return 'B', p[0], p[1], x['step'], evs
        if x['kind'] == 'EV':
            evs.append(x)
            continue
        return x['kind'], x, None, x.get('step'), evs
    return 'NONE', None, None, None, evs


def run_hs(L, A, nmoves, check=False, log=print, maxlit=10 ** 10, quiet_std=True):
    cnt = {}
    for it in range(nmoves):
        mv = std_move(L, A)
        if mv and not check:
            k, L, A = mv
            cnt[k] = cnt.get(k, 0) + 1
            continue
        kind, L2, A2, st, evs = literal_next(L, A, maxlit)
        if kind != 'B':
            log('END %s after %s: from [%s | %d]: %s' % (kind, cnt, fmt(L), A, show(L2) if isinstance(L2, dict) else L2))
            return kind, L, A, L2
        if mv:
            k, M, A3 = mv
            if (M, A3) != (L2, A2):
                log('MISMATCH %s: [%s | %d] -> lit [%s | %d] vs rule [%s | %d]' % (k, fmt(L), A, fmt(L2), A2, fmt(M), A3))
                return 'MISMATCH', L, A, None
            cnt[k] = cnt.get(k, 0) + 1
        else:
            log('SPECIAL (after %s) [%s | %d] -> [%s | %d]  %d steps, %d E0' % (cnt, fmt(L), A, fmt(L2), A2, st, len(evs)))
            cnt = {}
        L, A = L2, A2
    log('BUDGET %s [%s | %d]' % (cnt, fmt(L), A))
    return 'BUDGET', L, A, None


if __name__ == '__main__':
    from btrace import parse_list
    _, ts, A = sys.argv[1].split(':')
    run_hs(parse_list(ts), int(A), int(float(sys.argv[2])), check=len(sys.argv) > 3)
