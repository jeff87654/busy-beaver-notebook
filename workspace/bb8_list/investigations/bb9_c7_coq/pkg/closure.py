"""Dependency closure of c7/probe.v in bb9_c7_coq (logical paths XL, XDev, XScore, C7, BB8) -> topological list."""
import re, os, sys
W = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7_coq'
MAP = {'XL': 'x/lib', 'XDev': 'x/dev', 'XScore': 'x/score', 'C7': 'c7', 'BB8': 'lib9'}
F3LIB = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\ext\tree\lib'
def path(lp, name):
    if lp == 'BB8': return os.path.join(F3LIB, name + '.v'), 'lib9/' + name
    return os.path.join(W, MAP[lp], name + '.v'), MAP[lp].replace('x/', '') + '/' + name
def deps(fn):
    s = open(fn, encoding='utf-8').read()
    s = re.sub(r'\(\*.*?\*\)', '', s, flags=re.S)
    out = []
    for m in re.finditer(r'From\s+(\w+)\s+Require\s+(?:Import\s+|Export\s+)?([^.]*)\.', s):
        if m.group(1) in MAP:
            for nm in m.group(2).split():
                out.append(path(m.group(1), nm))
    return out
order = []; seen = {}
def visit(fn, key):
    if key in seen: return
    seen[key] = None
    ds = deps(fn)
    for f2, k2 in ds: visit(f2, k2)
    seen[key] = [k for _, k in ds]
    order.append((key, fn))
visit(os.path.join(W, 'c7', 'probe.v'), 'probe')
for k, fn in order:
    print(k, fn, ' '.join(seen[k]))
