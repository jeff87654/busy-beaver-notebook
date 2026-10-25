"""tr1.py L P s y t [steps]: K-moment D-views from D0(l,s,y,P,L,t) (my L), far l = 11 D(9) D(13)."""
import sys, subprocess, os
sys.path.insert(0, '../tools')
from lit import *
L, P, s, y, t = map(int, sys.argv[1:6]); steps = sys.argv[6] if len(sys.argv) > 6 else '3e8'
l = '11' + (tok(9) + tok(13))[:-1]
S = D0(l, s, y, P, L, t)
fs = 'st_%d.txt' % os.getpid(); open(fs, 'w').write(S)
out = subprocess.run(['../tools/c04raw.exe', '@file:%s:B' % fs, '--kmom', '--dv', '--steps', steps, '--width', '3000'], capture_output=True, text=True).stdout
os.remove(fs)
print(out)
