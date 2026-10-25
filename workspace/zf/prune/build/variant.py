"""zf/prune: make an ILS init from B354.json with clauses REPL (list) removed and NEW (Polish C/N formula over
p,q,r, roles a,b,c) inserted at the first removed clause's position.  Registers NEW in extra_spec.json.
usage: python variant.py POLISH REPL(comma) OUT.json"""
import sys, json, os
pol, repl, out = sys.argv[1], sys.argv[2].split(','), sys.argv[3]
def rpn(s):
    pos = 0
    def go():
        nonlocal pos
        c = s[pos]; pos += 1
        if c == 'C': return go() + go() + ['wim']
        if c == 'N': return go() + ['wn']
        return ['abc'['pqr'.index(c)]]
    t = go(); assert pos == len(s); return ' '.join(t)
name = 'Y_' + pol
ex = json.load(open('extra_spec.json')) if os.path.exists('extra_spec.json') else {}
ex[name] = rpn(pol); json.dump(ex, open('extra_spec.json', 'w'), indent=1)
b = json.load(open('B354.json'))
cl = b['clauses']; order = [cl[i] for i in b['order']]
first = min(order.index(r) for r in repl)
neworder = [c for c in order[:first]] + [name] + [c for c in order[first:] if c not in repl]
neworder = [c for c in neworder if c not in repl]
ncl = [c for c in cl if c not in repl] + [name]
b2 = dict(b); b2['clauses'] = ncl; b2['order'] = [ncl.index(c) for c in neworder]
b2['perm'] = {k: v for k, v in b['perm'].items() if k not in repl}
json.dump(b2, open(out, 'w'), indent=1); print(name, ex[name], neworder)
