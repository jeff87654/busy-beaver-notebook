"""mkph3.py K [mult...] : --kt spec of the post-J3 C04 configuration with every quantity = its real residue mod 5^K,
   lifted by multiples of 5^K to respect the real size order k3 < y4 < y3 < y2 < y1, k3 < y1 << R3 << P (default lifts 1,2,3,5,8,12,20: k3 < y4 < y3 < y2 < y1 < R3 < P)"""
import sys, subprocess
K = int(sys.argv[1]); M = 5 ** K
lift = [int(x) for x in sys.argv[2:]] or [1, 2, 3, 5, 8, 12, 20]
v = dict(l.split() for l in subprocess.run([sys.executable, 'c04res.py', str(K)], capture_output=True, text=True).stdout.split('\n') if l)
v = {k: int(x) for k, x in v.items()}
k3, y4, y3, y2, y1, R3, P = [v[n] + M * L for n, L in zip(['k3', 'y4', 'y3', 'y2', 'y1', 'B', 'P'], lift)]
print('0,0,%d,4,%d,6,%d,6,%d,1*%d,0,2,z2,1*%d;1;%d;18' % (y1, y2, y3, y4, P, k3, 3 * R3 + 2))
