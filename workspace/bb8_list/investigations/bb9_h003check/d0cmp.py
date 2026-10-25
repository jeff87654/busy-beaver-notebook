import idle
"""d0cmp.py OUT K1,.. T1,.. R1,..: h003 vs M8 from the exit Top(K): first two D0f moments (t, L, P, y, s, far view) and the
first CL view.  Expect: identical except y(h003) = y(M8)+1 at the first D0, P(h003) = P(M8)+2 afterwards."""
import sys, subprocess, re
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_h003check\hsim2.exe'
H = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC'; M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---'
out = open(sys.argv[1], 'a'); good = bad = 0
for R in map(int, sys.argv[4].split(',')):
    for T in map(int, sys.argv[3].split(',')):
        for K in map(int, sys.argv[2].split(',')):
            res = []
            for m in (H, M):
                p = subprocess.run([EXE, m, '--kt', '0,0,7,1*%d;1;1100;%d' % (K - 1, T), '--R', str(R), '--Rdef', '366', '--d0', '2',
                                    '--maxj', '2', '--ev', '0', '--view', '40'], capture_output=True, text=True, creationflags=0x40)
                d0 = [re.sub(r'step=\d+ ', '', l) for l in p.stdout.splitlines() if l.startswith('D0')]
                cl = [l.split('|')[1].strip() for l in p.stdout.splitlines() if l.startswith('CL 2')]
                res.append((d0, cl))
            (dh, ch), (dm, cm) = res
            def f(l): return dict(re.findall(r'(\w)=(\d+)', l.split('|')[0])), l.split('|')[1].strip()
            try:
                (a1, fa1), (b1, fb1) = f(dh[0]), f(dm[0])
                (a2, fa2), (b2, fb2) = f(dh[1]), f(dm[1])
                ok1 = all(a1[k] == b1[k] for k in 'tLPs') and int(a1['y']) == int(b1['y']) + 1 and fa1 == fb1
                ok2 = all(a2[k] == b2[k] for k in 'tLys') and int(a2['P']) == int(b2['P']) + 2 and fa2 == fb2
            except Exception as e:
                ok1 = ok2 = False
            ok = ok1 and ok2; good += ok; bad += not ok
            line = 'K=%d K%%25=%d T=%d R=%d %s | h003 %s || M8 %s' % (K, K % 25, T, R, 'OK' if ok else 'DIFF', ' ; '.join(dh), ' ; '.join(dm))
            out.write(line + '\n'); out.flush()
            if not ok: print(line[:400], flush=True)
print('ok', good, 'diff', bad)
