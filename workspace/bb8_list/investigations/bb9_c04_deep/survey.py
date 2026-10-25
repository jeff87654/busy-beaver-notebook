"""survey.py PREFIX R0 K0 K1 [t] [Rstep] : endgame survey in a context.  For k in [K0,K1): start Kt [PREFIX, 1^k] m=1 r=3*R0+2 t,
Rlist = R0+Rstep, R0+2Rstep, ... (increasing fresh accumulators), up to 12 jumps; print the outcome sequence."""
import subprocess, sys, re
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
pre, R0, k0, k1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
t = int(sys.argv[5]) if len(sys.argv) > 5 else 18; Rs = int(sys.argv[6]) if len(sys.argv) > 6 else 1000
P = max([int(x) for x in re.findall(r'1\*(\d+)', pre)] or [0])
RL = ','.join(str(R0 + Rs * i) for i in range(1, 13))
for k in range(k0, k1):
    o = subprocess.run(['./pkf4.exe', M, '--kt', '%s,1*%d;1;%d;%d' % (pre, k, 3 * R0 + 2, t), '--Rlist', RL, '--R', str(R0 + 13 * Rs), '--rmod', '36',
                        '--exactcap', '1000', '--jumps', '12', '--view', '400', '--maxs', '2e11', '--maxt', '2e11'], capture_output=True, text=True).stdout
    seq = []; last = ''
    for l in o.split('\n'):
        if l.startswith('J'):
            f = l.split('|')[0].split(); kind = f[1]
            if kind == 'CL':
                kk = int(re.search(r' k=(\d+)', l).group(1)); seq.append(('ESC%d' % kk) if kk > P / 2 else 'C%d' % kk)
            else: seq.append('R1')
            last = l.split('|')[1].strip()
        elif l.startswith('HALT'): seq.append('HALT'); 
        elif l.startswith(('STOP', 'END')): seq.append(l.split()[0])
    print(k, ' '.join(seq), '|', last[-150:], flush=True)
