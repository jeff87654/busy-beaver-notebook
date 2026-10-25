import sys, subprocess, os
sys.path.insert(0,'../tools')
from lit import D0, tok, T
L,P,s,y,t,lspec = sys.argv[1:7]
L,P,s,y,t=map(int,(L,P,s,y,t))
l = '11' + lspec  # lspec raw bits far..near after the 11
S=D0(l,s,y,P,L,t); fs='q%d.txt'%os.getpid(); open(fs,'w').write(S)
o=subprocess.run(['../tools/c04raw.exe','@file:%s:B'%fs,'--kmom','--steps','3e8','--width','100000'],capture_output=True,text=True).stdout
os.remove(fs); sys.stdout.write(o)
