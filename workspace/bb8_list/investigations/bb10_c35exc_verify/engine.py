"""engine.py -- symbolic accelerated simulation of B-form token lists (exact or huge values).

R(s): run the suffix s = [s_0, ..., s_m, 0, y] (tokens left of s_0 unknown) until the next event needs a
token left of s_0; return the suffix at that moment.  Recursive on s[1:], memoized on the residue state,
with exact cycle jumps on the counter s_0 when it is large (the state of s[1:] repeats while s_0 only
decreases by fixed amounts).
"""
import sys
from num import H, M, add, res, ge, key, is_huge
import rules
import oracle
USE_ORACLE = True

sys.setrecursionlimit(100000)
memo = {}
stats = {'calls': 0, 'jumps': 0, 'events': 0}
from collections import deque
TRACE = deque(maxlen=400)
TRACE_BIG = deque(maxlen=400)
TRACE_TOP = []
BIGLEN = 30
BIGC = 1000          # counters >= BIGC get cycle detection
MAXLOOP = 200000     # safety: events at one level without a jump


class NeedLeft(Exception):
    pass


def classify_suffix(s, top=False):
    """classify the next event of suffix s; returns Event or None if it needs tokens left of s.
    An unknown pattern below the top level is deferred to the parent (more left context)."""
    try:
        ev = rules.classify(s)
    except rules.Need:
        return None
    except rules.Unknown as e:
        if USE_ORACLE:
            try:
                ev = oracle.oracle_event(s)
            except rules.Need:
                return None
            except rules.Unknown as e2:
                if not top:
                    return None
                ex = rules.Unknown(str(e2) + ' | list=' + ' '.join(map(str, s)))
                ex.lst = list(s)
                raise ex
            return ev if ev.lo >= 0 else None
        if not top:
            return None
        raise rules.Unknown(str(e) + ' | list=' + ' '.join(map(str, s)))
    if ev.lo < 0:
        return None
    return ev


def skey(s):
    return tuple(key(v) for v in s)


def R(s, top=False):
    s = list(s)
    k0 = skey(s) + (top,)
    if k0 in memo:
        return list(memo[k0])
    stats['calls'] += 1
    if len(s) <= 2:
        memo[k0] = tuple(s)
        return s
    hist = {}
    dec_total = 0
    loops = 0
    while True:
        sub = R(s[1:])
        s = [s[0]] + sub
        ev = classify_suffix(s, top)
        if ev is None:
            memo[k0] = tuple(s)
            return s
        assert ev.lo == 0, (ev.name, ev.lo)
        stats['events'] += 1
        TRACE.append(('EV', len(s), ev.name, tuple(s)))
        if top:
            TRACE_TOP.append(('EV', ev.name, tuple(s), tuple(ev.newlist)))
        if len(s) >= BIGLEN:
            TRACE_BIG.append(('EV', len(s), ev.name, tuple(s)))
        loops += 1
        if loops > MAXLOOP:
            raise RuntimeError('no cycle at level with counter %r len %d' % (s[0], len(s)))
        x0 = s[0]
        large = is_huge(x0) or x0 >= BIGC
        if large and ev.name != 'R1*':
            kk = (ev.name, skey(s[1:]))
            if kk in hist:
                d = dec_total - hist[kk]
                if d <= 0:
                    raise RuntimeError('cycle without decrement')
                B = d + 50
                if is_huge(x0):
                    assert M % d == 0, ('period decrement not dividing M', d)
                    xr = B + (res(x0, d) - B) % d
                else:
                    xr = B + (x0 - B) % d if x0 >= B else x0
                stats['jumps'] += 1
                TRACE.append(('JUMP', len(s), d, tuple(s)))
                if len(s) >= BIGLEN:
                    TRACE_BIG.append(('JUMP', len(s), d, tuple(s)))
                s[0] = xr
                hist = {}
                continue
            hist[kk] = dec_total
        new = ev.newlist
        nx0 = new[0]
        if not is_huge(x0) and not is_huge(nx0):
            dec_total += x0 - nx0
        else:
            # huge counter: decrement known from the rule (difference of residues)
            dec_total += (res(x0, M) - res(nx0, M)) % M if is_huge(nx0) else 0
        s = list(new)
