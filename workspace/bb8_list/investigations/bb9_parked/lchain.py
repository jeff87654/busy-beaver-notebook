"""lchain.py N0 N1 R2 [prefix] [t] : the L-sequence of the C04 exhaustion chain.  For each n, start at Kt [prefix,1^n] m=1
r=3*R2+2 t (ktr.exe, literal) and record the D0-run lengths L at the sub-step moments ('| 0*L | m=0 r=0'), until the first
moment with m=1 r=2 (chain end).  Prints n, L-sequence, end t, end view."""
import subprocess, sys, re
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
n0, n1, R2 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
pre = sys.argv[4] if len(sys.argv) > 4 else '0,0'; t0 = int(sys.argv[5]) if len(sys.argv) > 5 else 3
for n in range(n0, n1):
    p = subprocess.Popen(['./ktr.exe', M, '--far', '-', '--kt', '%s,1*%d;1;%d;%d' % (pre, n, 3 * R2 + 2, t0), '--nk', '100000',
                          '--maxs', '2e10'], stdout=subprocess.PIPE, text=True)
    Ls = []; end = '?'
    for line in p.stdout:
        m = re.search(r'\| 0\*(\d+) \| m=0 r=0 t=(\d+)', line)
        if m: Ls.append(int(m.group(1))); continue
        if 'm=1 r=2' in line or line.startswith(('HALT', 'STOP')):
            end = line.split('|', 1)[1].split('used=')[0].strip() if '|' in line else line.strip(); break
    p.kill()
    print(n, ' '.join(map(str, Ls)), '||', end[:200], flush=True)
