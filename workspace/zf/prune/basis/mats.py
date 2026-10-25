"""All 3-valued matrices (->, -., designated D) closed under MP in which B1 is valid; for each record whether
B2, B3 are valid.  Saved to mats3.pkl.  Used as a filter: an axiom Y such that {B1, Y} is complete must fail
in every matrix where B2 or B3 fails."""
import sys, itertools, pickle
sys.path.insert(0, '..'); import lowprio  # noqa
nv = 3; vals = range(nv); out = []
Ds = [set(c) for r in range(1, nv) for c in itertools.combinations(vals, r)]
for It in itertools.product(vals, repeat=nv*nv):
    I = [It[i*nv:(i+1)*nv] for i in vals]
    for D in Ds:
        if any(a in D and I[a][b] in D and b not in D for a in vals for b in vals): continue
        b1 = all(I[I[a][b]][I[I[b][c]][I[a][c]]] in D for a in vals for b in vals for c in vals)
        for N in itertools.product(vals, repeat=nv):
            b2 = all(I[I[N[a]][a]][a] in D for a in vals)
            b3 = all(I[a][I[N[a]][b]] in D for a in vals for b in vals)
            if not (b2 and b3): out.append((I, N, frozenset(D), b1, b2, b3))
pickle.dump(out, open('mats3.pkl', 'wb')); print(len(out))
