import sys,re
# tokenise bit string: runs of '10' counted, other tokens shown
for line in sys.stdin:
    line=line.strip()
    if ' ' not in line: print(line); continue
    st,s=line.split(' ',1)
    out=[];i=0
    while i<len(s):
        if s.startswith('10',i):
            k=0
            while s.startswith('10',i): k+=1;i+=2
            out.append('a%d'%k)
        elif s.startswith('110',i): out.append('c');i+=3
        elif s.startswith('1',i) and i+1<len(s) and s[i+1]=='1': out.append('1');i+=1
        elif s[i]=='0': out.append('0');i+=1
        else: out.append('1');i+=1
    print(st,len(s),' '.join(out))
