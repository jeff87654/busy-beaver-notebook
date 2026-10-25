import sys, subprocess
from tokv import *
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
word,N,f,l = sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
out = subprocess.run(['./snap.exe',M,word,'B',N,f,l],capture_output=True,text=True).stdout
for line in out.splitlines():
    p=line.split()
    if len(p)==2 and p[0].isdigit():
        print(p[0], rl(tokview(p[1]))[:700])
    else: print(line[:300])
