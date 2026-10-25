"""probe.py MACHINE 'ds;a;b' ... : print next NCHG ds-changes (env NCHG=2, STEPS=1e8)."""
import idle, sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short
M = sys.argv[1]; TT = kl.tmpl(M, os.environ['TMPL']) if os.environ.get('TMPL') else None; N = int(os.environ.get('NCHG', '2')); ST = int(float(os.environ.get('STEPS', '1e8')))
for spec in sys.argv[2:]:
    d, a, b = spec.split(';'); ds = [int(x) for x in d.split(',') if x]
    ev = kl.run(M, ds, int(a), int(b), ST, N + 1, 400, T=TT)
    out = []
    for e in ev[1:]:
        if e[0] == 'K': out.append(f'[{short(e[2])};{e[3]};{e[4]}]@{e[1]}')
        elif e[0] == 'H': out.append(f'HALT@{e[1]}{e[2]}{e[3]}')
        elif e[0] == 'END': out.append('END')
    print(f'[{spec}] ->', ' '.join(out), flush=True)
