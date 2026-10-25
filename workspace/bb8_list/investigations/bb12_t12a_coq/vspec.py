"""vspec.py: write B-form specs as view strings (left-to-right), e.g.
  'L 2^{K} 2^6 1 T{15,x} 0^6 z2 0 z5 [0 9 z2 0^6 z2 0^3 z4 4 9 0 1^4]^{j} 2 4 0 T{0,A} 1^3 0 1^3 0 6'
items: L (the far side l, first item only) | m (token D m) | m^c | zN (N zeros) | T{c,v} (token D(c+v)) |
       T3{c,v} (token D(c+3v)) | T9{c,v} (D(c+9v)) | m^{v} (run of D m tokens, m in 1,2) | [view]^{v} (run of raw cells)."""
import re
from shapes import *
from planner8 import V

def cells_lr(items):
    """left-to-right cells of constant items"""
    out = []
    for it in items:
        if it.startswith('z'):
            out += [0] * int(it[1:])
        else:
            if '^' in it:
                m, c = it.split('^'); m, c = int(m), int(c)
            else:
                m, c = int(it), 1
            out += ([1, 0] * m + [1]) * c
    return out

def split_items(s):
    out = []; i = 0; s = s.strip()
    while i < len(s):
        if s[i] == ' ':
            i += 1; continue
        if s[i] == '[':
            d = 0; j = i
            while True:
                if s[j] == '[': d += 1
                if s[j] == ']':
                    d -= 1
                    if d == 0: break
                j += 1
            m = re.match(r'\^\{(\w+)\}', s[j + 1:])
            out.append(('RUN', s[i + 1:j], m.group(1)))
            i = j + 1 + m.end(); continue
        j = i
        while j < len(s) and s[j] != ' ':
            j += 1
        out.append(s[i:j]); i = j
    return out

def vs(s):
    """view string -> W(...) start/target config (head in H at the right end)"""
    items = split_items(s)
    far = [BLANK]
    if items and items[0] == 'L':
        far = [V('l')]; items = items[1:]
    toks = []
    for it in items:
        if isinstance(it, tuple):
            cl = cells_lr(split_items(it[1]))
            toks.append([run(tuple(reversed(cl)), **{it[2]: 1})])
            continue
        m = re.match(r'^(T|T3|T9)\{(\d+),(\w+)\}$', it)
        if m:
            c, v = int(m.group(2)), m.group(3)
            if m.group(1) == 'T':
                toks.append(tok(c, **{v: 1}))
            else:
                k = 3 if m.group(1) == 'T3' else 9
                toks.append([1] + [0, 1] * c + [run((0, 1) * k, **{v: 1})])
            continue
        m = re.match(r'^(\d+)\^\{(\w+)\}$', it)
        if m:
            d = int(m.group(1))
            toks.append([run(tuple([1] + [0, 1] * d)[::-1], **{m.group(2): 1})])
            continue
        if it.startswith('z'):
            toks.append([0] * int(it[1:])); continue
        if '^' in it:
            mm, c = it.split('^')
            for _ in range(int(c)):
                toks.append(tok(int(mm)))
            continue
        toks.append(tok(int(it)))
    return W(*toks, far=far)
