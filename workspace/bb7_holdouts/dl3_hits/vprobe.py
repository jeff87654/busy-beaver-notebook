"""vprobe.py MACHINE TMPL BFIX 'v1,..,vn;A' ... : all-runs coding; print successive moments whose last run == BFIX (env N=3, STEPS)."""
import idle, sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short
M, TM, BF = sys.argv[1], sys.argv[2], int(sys.argv[3]); T = kl.tmpl(M, TM)
N = int(os.environ.get('N', '3')); ST = int(float(os.environ.get('STEPS', '1e7'))); ML = int(os.environ.get('ML', '200000'))
def nxt(ds, A, n=N):
    ev = kl.run(M, ds, A, BF, ST, 0, ML, T=T, pall=1)
    out = []
    for e in ev[1:]:
        if e[0] == 'K' and e[4] == BF: out.append((e[1], e[2], e[3]))
        elif e[0] == 'H': out.append((e[1], 'HALT', e[2] + str(e[3])))
        if len(out) >= n: break
    return out
if __name__ == '__main__':
    for spec in sys.argv[4:]:
        d, a = spec.split(';'); ds = [int(x) for x in d.split(',') if x]
        r = nxt(ds, int(a))
        print(f'[{spec}] ->', ' '.join(f'[{short(x[1])};{x[2]}]@{x[0]}' if x[1] != 'HALT' else f'HALT@{x[0]}{x[2]}' for x in r), flush=True)
