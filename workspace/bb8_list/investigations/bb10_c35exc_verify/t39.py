import engine, rules, oracle, pickle
from num import H, M, res, is_huge
from tower import tower_res
T = tower_res(M)
A = H(3 * T - 6)
s = [A] + [1] * 36 + [0, 6]
try:
    engine.R(s, top=True)
except rules.Unknown as e:
    pass
print('oracle cache entries:', len(oracle.cache))
for k, f in oracle.cache.items():
    print(k[-12:] if len(k) > 12 else k, '->', f if isinstance(f, str) else [x for x in f][-12:])
pickle.dump(dict(oracle.cache), open('oracle_cache.pkl', 'wb'))
