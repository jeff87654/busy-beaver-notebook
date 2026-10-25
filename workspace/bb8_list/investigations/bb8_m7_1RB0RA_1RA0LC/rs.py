import sys, subprocess, re
from comp import compress
# usage: rs.py WORD N first last
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
word,N,f,l = sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
out = subprocess.run(['./snap.exe',M,word,'B',N,f,l],capture_output=True,text=True).stdout
for line in out.splitlines():
    if ' ' in line and line.split()[0].isdigit():
        st, bits = line.split()
        print(st, compress(bits, 3, 8)[:600])
    else: print(line)
