"""eprobe.py MACHINE KLIST BLIST [STEPS] [NEV]: exhaustion probes E(k;b)=K(0^k;0;b) in the out.tsv template; print next NEV K-moments with a changed list."""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
from egrid import short
M = sys.argv[1]; KL = [int(x) for x in sys.argv[2].split(',')]; BL = [int(x) for x in sys.argv[3].split(',')]
ST = int(float(sys.argv[4])) if len(sys.argv) > 4 else 10**8; NE = int(sys.argv[5]) if len(sys.argv) > 5 else 2
T = kl.tmpl(M)
for k in KL:
    for b in BL:
        ev = kl.run(M, [0] * k, 0, b, ST, NE + 1, 400, T=T)
        out = []
        for e in ev[1:]:
            if e[0] == 'K': out.append(f'[{short(e[2])};{e[3]};{e[4]}]@{e[1]}')
            elif e[0] == 'H': out.append(f'HALT@{e[1]}')
            elif e[0] == 'END': out.append('END')
        print(f'E(k={k};b={b}) ->', ' '.join(out), flush=True)
