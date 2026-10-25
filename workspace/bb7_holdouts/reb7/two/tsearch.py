import idle, sys
sys.path.insert(0, '.')
import fit7
m = sys.argv[1]
found = []
for O in 'LR':
    for Q in 'ABCDEFG':
        for u in ('011', '110', '101', '01', '10', '1'):
            for s in ('0', '00', '1'):
                if s == u: continue
                for P in ('-', '1', '11', '111', '1111', '110', '101', '10'):
                    for S in ('-', '0', '1', '00', '01', '10', '11', '011', '110'):
                        for b in ('1b+0', '2b+0', '2b+1'):
                            t = '%s,%s,P=%s,u=%s,s=%s,d=1d+0,b=%s,S=%s' % (O, Q, P, u, s, b, S)
                            P_ = fit7.Prober(m, t)
                            ks, end = P_.trace(20000000, 60)
                            if len(ks) >= 50 and max(len(k[1]) for k in ks) >= 2:
                                found.append((len(ks), t))
                                print(len(ks), t, ks[-1][1][:8], ks[-1][2], ks[-1][3], flush=True)
