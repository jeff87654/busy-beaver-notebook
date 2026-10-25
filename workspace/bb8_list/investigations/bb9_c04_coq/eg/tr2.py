"""tr2.py L P s y t steps [dv]: K-moments from D0 (my L); far l = 11 D(9) D(13)."""
import sys, subprocess, os
sys.path.insert(0, '../tools')
from lit import *
L, P, s, y, t = map(int, sys.argv[1:6]); steps = sys.argv[6]
l = '11' + (tok(9) + tok(13))[:-1]
S = D0(l, s, y, P, L, t)
fs = 'st_%d.txt' % os.getpid(); open(fs, 'w').write(S)
args = ['../tools/c04raw.exe', '@file:%s:B' % fs, '--kmom', '--steps', steps, '--width', '3000']
if len(sys.argv) > 7: args.append('--dv')
out = subprocess.run(args, capture_output=True, text=True).stdout
os.remove(fs)
sys.stdout.write(out)
