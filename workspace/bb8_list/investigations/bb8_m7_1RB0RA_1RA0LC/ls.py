import sys, subprocess
from comp import compress
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
word,N,f,l = sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
out = subprocess.run(['./left.exe',M,word,'B',N,f,l],capture_output=True,text=True).stdout
for line in out.splitlines():
    p=line.split(' ',2)
    if len(p)==3 and p[0].isdigit():
        print(p[0],p[1], compress(p[2].replace('[','').replace(']','')  ,3,8)[:400])
    else: print(line[:300])
