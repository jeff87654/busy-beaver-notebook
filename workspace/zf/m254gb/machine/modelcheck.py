"""Brute-force model checking of role-named formulas (ngdsl ASTs) over small hereditarily finite
universes.  Sets are frozensets; von Neumann ordinals k = {0..k-1}.

check_formula(f, env, U): truth of f with free roles bound by env, quantifiers ranging over U.
Pattern ∃v (v = w ∧ B) (and ∀v (v = w → B)) is evaluated by direct binding (exact, any universe
containing w).  U should be transitive and contain every witness the formula needs.
"""
import itertools
from functools import lru_cache

def ordinal(k):
    s = frozenset()
    for _ in range(k):
        s = s | {s}
    return s

def powerset(S):
    S = list(S)
    return [frozenset(c) for r in range(len(S) + 1) for c in itertools.combinations(S, r)]

def universe(n):
    """n ∪ {n} ∪ P(n) ∪ P(P(n)) plus transitive closure (enough for NG' witnesses about n)."""
    U = set(n) | {n} | set(powerset(n))
    U |= set(powerset(powerset(n)))
    changed = True
    while changed:
        changed = False
        for x in list(U):
            for y in x:
                if y not in U: U.add(y); changed = True
    return sorted(U, key=lambda s: (len(s), repr(sorted(map(id, s)))))

def ev(f, env, U):
    if isinstance(f, str):
        if f == '<F>': return False
        raise ValueError(f)
    h = f[0]
    if h == 'el': return env[f[1]] in env[f[2]]
    if h == 'eq': return env[f[1]] == env[f[2]]
    if h == 'not': return not ev(f[1], env, U)
    if h == 'and': return ev(f[1], env, U) and ev(f[2], env, U)
    if h == 'or': return ev(f[1], env, U) or ev(f[2], env, U)
    if h == 'im': return (not ev(f[1], env, U)) or ev(f[2], env, U)
    v, body = f[1], f[2]
    # binding shortcuts
    if h == 'ex' and body[0] == 'and' and body[1][0] == 'eq' and body[1][1] == v and body[1][2] != v:
        e2 = dict(env); e2[v] = env[body[1][2]]
        return ev(body[2], e2, U)
    if h == 'ex' and body[0] == 'and' and body[1][0] == 'el' and body[1][1] == v and body[1][2] != v:
        dom = env[body[1][2]]
        for x in dom:
            e2 = dict(env); e2[v] = x
            if ev(body[2], e2, U): return True
        return False
    if (h == 'all' and body[0] == 'im' and body[1][0] == 'or' and body[1][1][0] == 'eq' and body[1][2][0] == 'eq'
            and body[1][1][1] == v and body[1][2][1] == v and v not in (body[1][1][2], body[1][2][2])):
        # ∀v ((v=a ∨ v=b) → B)
        for w in (body[1][1][2], body[1][2][2]):
            e2 = dict(env); e2[v] = env[w]
            if not ev(body[2], e2, U): return False
        return True
    if h == 'all' and body[0] == 'im' and body[1][0] == 'el' and body[1][1] == v and body[1][2] != v:
        dom = env[body[1][2]]
        for x in dom:
            e2 = dict(env); e2[v] = x
            if not ev(body[2], e2, U): return False
        return True
    if h == 'ex':
        for x in U:
            e2 = dict(env); e2[v] = x
            if ev(body, e2, U): return True
        return False
    if h == 'all':
        for x in U:
            e2 = dict(env); e2[v] = x
            if not ev(body, e2, U): return False
        return True
    raise ValueError(f)

def relabel(f, lab):
    if isinstance(f, str):
        return f if f == '<F>' else lab[f]
    h = f[0]
    if h in ('el', 'eq'): return (h, lab[f[1]], lab[f[2]])
    if h in ('all', 'ex'): return (h, lab[f[1]], relabel(f[2], lab))
    if h == 'not': return (h, relabel(f[1], lab))
    return (h, relabel(f[1], lab), relabel(f[2], lab))
