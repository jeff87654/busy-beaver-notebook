"""exh.py MACHINE n0 n1 [r] [t] : literal exhaustion probe.  For n in [n0, n1): start at
   Kt [0,0,1^n] m=1 r t (head in B on the blank right end) and run pkf.exe literally to the next jump moment; print the
   pre-jump token view (far -> near) with t and k.  Default r=2 (accumulator b=0), t=3."""
import subprocess, sys
M = sys.argv[1]; n0, n1 = int(sys.argv[2]), int(sys.argv[3]); r = int(sys.argv[4]) if len(sys.argv) > 4 else 2
t = int(sys.argv[5]) if len(sys.argv) > 5 else 3
for n in range(n0, n1):
    w = '11' + '101' * n + '101' + '10' * r + '11' + '11111100' * t + '1001'
    o = subprocess.run(['./pkf.exe', M, '--start', '%s:%d:B' % (w, len(w)), '--Rlist', '0', '--R', '0', '--jumps', '1', '--view', '600',
                        '--maxs', '2e10', '--maxt', '2e10', '--exactcap', '1000'], capture_output=True, text=True).stdout
    line = [l for l in o.split('\n') if l.startswith(('J1', 'HALT', 'STOP'))]
    l = line[0] if line else '?'
    if l.startswith('J1'):
        a = l.split('|')[0].split(); print(n, a[1], a[5], a[6], '|', l.split('|')[1].strip()[:400])
    else:
        print(n, l[:200])
