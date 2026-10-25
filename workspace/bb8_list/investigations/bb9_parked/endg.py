"""endg.py PREFIX R N0 N1 [t] : endgame survey.  For z in [N0,N1): start at Kt [PREFIX, 1^z] m=1 r=3R+2 t (pkf4 literal +
jumps, R fixed for later clears) and classify the first jump: RES (chain ended by residue: digit behind a near list),
ESC (cleared list longer than the parked list in PREFIX / 2), other CL, R1, HALT."""
import subprocess, sys, re, collections
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
pre, R, n0, n1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); t = int(sys.argv[5]) if len(sys.argv) > 5 else 18
P = max([int(x) for x in re.findall(r'1\*(\d+)', pre)] or [0])
cnt = collections.Counter()
for z in range(n0, n1):
    o = subprocess.run(['./pkf4.exe', M, '--kt', '%s,1*%d;1;%d;%d' % (pre, z, 3 * R + 2, t), '--R', str(R), '--jumps', '1', '--view', '300',
                        '--maxs', '1e11', '--maxt', '1e11', '--exactcap', '1000'], capture_output=True, text=True).stdout
    l = [x for x in o.split('\n') if x.startswith(('J1', 'HALT', 'STOP'))]
    l = l[0] if l else '?'
    if l.startswith('HALT'): c = 'HALT ' + l.split()[1]
    elif l.startswith('J1 CL'):
        k = int(re.search(r' k=(\d+)', l).group(1)); c = 'ESC' if k > P / 2 else 'RES/CL'
    elif l.startswith('J1 R1'): c = 'R1'
    else: c = l[:10]
    cnt[c] += 1
    print(z, c, '|', l.split('|')[-1].strip()[:160], flush=True)
print('SUMMARY', dict(cnt))
