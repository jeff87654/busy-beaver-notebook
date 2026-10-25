"""lemma.py : prove loop lemmas for F89 with msim (sound shift-rule symbolic simulation).
Spec strings: space separated tokens; 'w' literal cells; 'w^E' block of w repeated E times (E = linear expression in
symbols, e.g. 3*m+2); '[Q]' marks the head: it sits on the first cell of the next token.  Symbols are naturals with lower
bounds given in LB.  prove(start, stop, expect) runs from start until the stop event and compares the canonical tape."""
import re
import msim
from msim import Sim, Lin, Fail, lb


def expr(e):
    e = e.strip()
    tot = Lin.c(0)
    for term in re.findall(r'[+-]?[^+-]+', e):
        term = term.strip()
        sign = -1 if term.startswith('-') else 1
        term = term.lstrip('+-')
        if '*' in term:
            c, v = term.split('*')
            tot = tot + Lin({v: sign * int(c)})
        elif term.isdigit():
            tot = tot + Lin.c(sign * int(term))
        else:
            tot = tot + Lin({term: sign})
    return tot


def build(spec):
    items = []
    h = None
    q = None
    for tok in spec.split():
        m = re.match(r'^\[([A-G])\](.*)$', tok)
        if m:
            q = m.group(1)
            h = len(items)
            tok = m.group(2)
            if not tok:
                continue
        if '^' in tok:
            w, e = tok.split('^', 1)
            n = expr(e)
            if n.isconst():
                items += list(w * int(n.const()))
            else:
                items.append(['B', w, n])
        else:
            items += list(tok)
    if h is not None and not isinstance(items[h], str):
        raise Fail('head on block in spec')
    return items, h, q


def canon(items, h, q):
    """canonical form: list of ('L', char) / ('H', char, q) / ('B', w, Lin)."""
    seq = []
    for i, x in enumerate(items):
        if i == h:
            seq.append(('H', x, q))
        elif isinstance(x, str):
            seq.append(('L', x))
        else:
            if x[2].isconst():
                seq += [('L', c) for c in x[1] * int(x[2].const())]
            else:
                seq.append(('B', x[1], x[2]))
    changed = True
    while changed:
        changed = False
        for i, x in enumerate(seq):
            if x[0] != 'B':
                continue
            w, n = x[1], x[2]
            L = len(w)
            # absorb copy on the right
            if i + L < len(seq) and all(seq[i + 1 + j][0] == 'L' and seq[i + 1 + j][1] == w[j] for j in range(L)):
                seq[i:i + 1 + L] = [('B', w, n + 1)]
                changed = True
                break
            # absorb copy on the left
            if i - L >= 0 and all(seq[i - L + j][0] == 'L' and seq[i - L + j][1] == w[j] for j in range(L)):
                seq[i - L:i + 1] = [('B', w, n + 1)]
                changed = True
                break
            # rotate: literal c before block with c == w[-1]: c (u c)^n -> (c u)^n c
            if i >= 1 and seq[i - 1][0] == 'L' and seq[i - 1][1] == w[-1]:
                c = w[-1]
                seq[i - 1:i + 1] = [('B', c + w[:-1], n), ('L', c)]
                changed = True
                break
            # merge with next block of same word
            if i + 1 < len(seq) and seq[i + 1][0] == 'B' and seq[i + 1][1] == w:
                seq[i:i + 2] = [('B', w, n + seq[i + 1][2])]
                changed = True
                break
    # minimal period of block words
    out = []
    for x in seq:
        if x[0] == 'B':
            w = x[1]
            for p in range(1, len(w) + 1):
                if len(w) % p == 0 and w[:p] * (len(w) // p) == w:
                    break
            if p < len(w):
                x = ('B', w[:p], x[2] * (len(w) // p))
        out.append(x)
    return out


def cstr(c):
    s = []
    for x in c:
        if x[0] == 'L':
            s.append(x[1])
        elif x[0] == 'H':
            s.append('[%s]%s' % (x[2], x[1]))
        else:
            s.append(' %s^{%r} ' % (x[1], x[2]))
    return ''.join(s)


def ceq(a, b):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x[0] != y[0]:
            return False
        if x[0] == 'B':
            if x[1] != y[1] or not (x[2] == y[2]):
                return False
        elif x != y:
            return False
    return True


def prove(name, start, stop, expect, nstop=1, maxsteps=10 ** 6):
    items, h, q = build(start)
    s = Sim(items, h, q)
    try:
        for _ in range(nstop):
            ev = s.run_pred(stop, maxsteps) if getattr(stop, 'pred', False) else s.run(stop, maxsteps)
            if ev[0] == 'HALT':
                return False, 'HALT'
    except Fail as e:
        return False, 'FAIL %s' % e
    got = canon(s.t, s.h, s.q)
    ei, eh, eq = build(expect)
    exp = canon(ei, eh, eq)
    ok = ceq(got, exp)
    return ok, cstr(got) + ('' if ok else '   EXPECTED ' + cstr(exp)) + ' rnew=%d' % getattr(s, 'rnew', 0)
