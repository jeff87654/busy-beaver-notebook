import idle, sys, time
import fit7, eng7, rounds7
m, t = sys.argv[1], sys.argv[2]
P = fit7.Prober(m, t)
R = fit7.fit_rules(P)
pat, E, _ = fit7.fit_E(P, 0, 60)
print('E', pat, E)
ks, end = P.trace(300000000, 3000)
print('trace', len(ks), end, ks[0] if ks else None, ks[-1][0] if ks else None)
# literal exhaustions in trace
for Q in (20160, 443520):
    t0=time.time()
    eng = eng7.Eng(R, Q=Q)
    s = ks[-1]
    V = eng.value(s[1], s[2], s[3])
    v, tr = rounds7.run_rounds(eng, E, V)
    print('Q', Q, 'V1', V, v, tr[:8], 'period', eng.period, 'flags', eng.flags[:3], 'pre', eng.precond[:3], '%.1fs'%(time.time()-t0))
