"""survey2.py PREFIX R0 K0 K1 STEP [t] [Rstep] [jumps] : like survey.py but k in range(K0,K1,STEP), fewer jumps, prints class guess."""
import subprocess, sys, re
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
pre, R0, k0, k1, st = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
t = int(sys.argv[6]) if len(sys.argv) > 6 else 18; Rs = int(sys.argv[7]) if len(sys.argv) > 7 else 100; J = int(sys.argv[8]) if len(sys.argv) > 8 else 5
P = max([int(x) for x in re.findall(r'1\*(\d+)', pre)] or [0])
RL = ','.join(str(R0 + Rs * i) for i in range(1, J + 1))
for k in range(k0, k1, st):
    o = subprocess.run(['./pkf4.exe', M, '--kt', '%s,1*%d;1;%d;%d' % (pre, k, 3 * R0 + 2, t), '--Rlist', RL, '--R', str(R0 + (J + 2) * Rs), '--rmod', '36',
                        '--exactcap', '1000', '--jumps', str(J), '--view', '400', '--maxs', '2e11', '--maxt', '2e11'], capture_output=True, text=True).stdout
    seq = []; last = ''; esc = False; cls = '?'
    for l in o.split('\n'):
        if l.startswith('J'):
            f = l.split('|')[0].split(); kind = f[1]
            if kind == 'CL':
                kk = int(re.search(r' k=(\d+)', l).group(1)); seq.append(('ESC%d' % kk) if kk > P / 2 else 'C%d' % kk)
                if kk > P / 2: esc = True
            else: seq.append('R1')
            last = l.split('|')[1].strip()
        elif l.startswith('HALT'): seq.append('HALT'); cls = 'b' if esc else 'a'
        elif l.startswith(('STOP', 'END')): seq.append(l.split()[0]); cls = 'c' if esc else 'cont'
    print(k, cls, ' '.join(seq), '|', last[-120:], flush=True)
