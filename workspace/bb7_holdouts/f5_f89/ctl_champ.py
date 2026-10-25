# control (a): symsim must find the BB(7) champion's halting exhaustion [0^11, X] (C1 coding, TF [0,3,0,1], K state B right)
import subprocess
S = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit\src\symsim.exe'
m = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF'
for n0 in (1, 11):
    out = []
    for r in range(12):
        tp = '11 ' + ' 1 ' * n0 + ' 10^H%d 0 1^3 0 0 1 B>' % r
        tp = ' '.join(tp.split())
        p = subprocess.run([S, 'run', '--noch', '--nokt', '--mg', '720', '--budget', '2000000', '--stopq', 'B', '--stopn', '3', '--hlb', '1000', '--tlimit', '60'],
                           input='%s B %s\n' % (m, tp), capture_output=True, text=True)
        v = [l.split()[3] for l in p.stdout.splitlines() if l.startswith('R ')]
        out.append((r, v[0] if v else '?'))
    print('champion exhaustion [0^%d, X], X = r mod 720 >= 1000:' % n0, out, flush=True)
