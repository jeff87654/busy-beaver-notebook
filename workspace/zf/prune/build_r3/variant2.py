"""zf/prune: init from BASE.json with clauses REPL removed and NEW (an extra_spec name) inserted at the
first removed clause's position.  usage: python variant2.py BASE.json NEW REPL(comma) OUT.json"""
import sys, json
base, name, repl, out = sys.argv[1], sys.argv[2], sys.argv[3].split(','), sys.argv[4]
b = json.load(open(base))
cl = b['clauses']; order = [cl[i] for i in b['order']]
first = min(order.index(r) for r in repl)
neworder = [c for c in order[:first]] + [name] + [c for c in order[first:] if c not in repl]
ncl = [c for c in cl if c not in repl] + [name]
b2 = dict(b); b2['clauses'] = ncl; b2['order'] = [ncl.index(c) for c in neworder]
b2['perm'] = {k: v for k, v in b['perm'].items() if k not in repl}
json.dump(b2, open(out, 'w'), indent=1); print(neworder)
