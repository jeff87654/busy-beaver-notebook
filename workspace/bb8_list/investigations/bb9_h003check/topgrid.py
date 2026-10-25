import idle
"""topgrid.py OUT K1,K2,.. T1,T2,.. RLIST[;RLIST2..]: start h003 at the Top(K) CL moment '0*2 7 1*K' (r = 3b+2 with b = 366,
t = T), CL accumulators from RLIST (first = the clear of Top(K) itself), follow until the next Top view '0*2 7 1*K'' or a
non-rebuild view.  Prints the intermediate CL views and K', and which R of the list K' uses under the fitted rules."""
import sys, subprocess, re
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_h003check\hsim.exe'
H = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC'
RULE = {1: (9, 36), 4: (3, -2), 3: (3, 16)}
out = open(sys.argv[1], 'a')
Ks = [int(x) for x in sys.argv[2].split(',')]
Ts = [int(x) for x in sys.argv[3].split(',')]
RLs = sys.argv[4].split(';')
B = int(sys.argv[5]) if len(sys.argv) > 5 else 366
for RL in RLs:
    Rs = [int(x) for x in RL.split(',')]
    for T in Ts:
        for K in Ks:
            p = subprocess.run([EXE, H, '--kt', '0,0,7,1*%d;1;%d;%d' % (K - 1, 3 * B + 2, T), '--R', RL, '--Rdef', '366',
                                '--maxj', '2' if K % 5 in (0, 2) else '6', '--stoptop', '--maxs', '4e10', '--ev', '0', '--view', '300'], capture_output=True, text=True,
                               creationflags=0x40)
            L = [l for l in p.stdout.splitlines() if l.startswith('CL')]
            inter, nxt = [], None
            for l in L[1:]:
                v = l.split('|', 1)[1].strip()
                m = re.fullmatch(r'0\*2 7 1\*(\d+)', v)
                tt = re.search(r' t=(\d+)', l).group(1)
                if m: nxt = (int(m.group(1)), int(tt)); break
                inter.append(v)
                if not v.startswith('0 1 '): break
            r = K % 5
            info = ''
            if nxt and r in RULE:
                a, c = RULE[r]; num = 5 * nxt[0] - a * K - c
                used = num / 60
                idx = [i for i, R in enumerate(Rs) if R == used]
                info = 'Rused=%s idx=%s' % (used, idx)
            line = 'K=%d K%%5=%d K%%25=%d K%%3=%d t=%d R=%s -> %s %s | inter: %s' % (
                K, K % 5, K % 25, K % 3, T, RL, ('TOP %d t=%d' % nxt) if nxt else 'EXIT', info, ' || '.join(x[:120] for x in inter))
            print(line, flush=True); out.write(line + '\n'); out.flush()
