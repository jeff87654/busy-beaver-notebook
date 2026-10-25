"""casc.py J0 J1 [mult] : C04 cascade experiment in a size-faithful world.  For n = 1792 + 3125 j (the real class of
n = 12B+25 mod 5^5), start at exhaustion #2 (Kt [0,0,1^n] m=1 r=3R2+2 t=3) with R2 = 20 n (parked list 12R2-10 >> rest),
every later JCL accumulator R = 5n (>> the y tokens ~0.6n, << the parked list) for 40 clears, and stop at the first jump
whose cleared list is the parked list (k > 6 R2 : 'ESC') or at a halt / step cap.  Prints per n: outcome, #jumps, t, k's."""
import subprocess, sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
j0, j1 = int(sys.argv[1]), int(sys.argv[2]); mult = int(sys.argv[3]) if len(sys.argv) > 3 else 5
for j in range(j0, j1):
    n = 1792 + 3125 * j; R2 = 20 * n; R = mult * n
    cmd = ['./pkf3.exe', M, '--kt', '0,0,1*%d;1;%d;3' % (n, 3 * R2 + 2), '--Rlist', ','.join([str(R)] * 40), '--R', str(R),
           '--rmod', '36', '--exactcap', '1000', '--jumps', '60', '--view', '300', '--maxs', '2e12', '--maxt', '2e12']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    ks = []; out = 'CAP'; t = '?'
    for line in p.stdout:
        if line.startswith('J'):
            f = line.split('|')[0].split(); kind = f[1]; t = f[4]
            k = int(f[5][2:]) if kind == 'CL' else -1
            ks.append(k if kind == 'CL' else 'R1')
            if kind == 'CL' and k > 6 * R2:
                out = 'ESC'; break
        elif line.startswith('HALT'):
            out = 'HALT ' + line.split()[1]; break
        elif line.startswith(('STOP', 'END')):
            out = line.split()[0]; break
    p.kill()
    print(n, out, 'jumps', len(ks), t, 'ks', ks[:30], flush=True)
