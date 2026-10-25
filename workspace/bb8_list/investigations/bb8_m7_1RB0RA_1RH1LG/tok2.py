import sys
# like tok.py but compresses repeats of single tokens: 1^n, 0^n, c^n
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
        else: out.append(s[i]); i+=1
    comp=[];j=0
    while j<len(out):
        k=j
        while k<len(out) and out[k]==out[j]: k+=1
        comp.append(out[j] if k-j==1 else '%s^%d'%(out[j],k-j)); j=k
    print(st,len(s),' '.join(comp))
