import re,sys
from lit import parse,M
t=parse(M);tape={};p=0;s=0;lo=0
P=re.compile(r'^0((?:100)*)10((?:100)*)(1*)$')
Q=re.compile(r'^0((?:100)*)10((?:100)*)101(1*)$')
prev=None;
for k in range(int(sys.argv[1])):
    v=tape.get(p,0);r=t[(s,v)]
    tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
    if p<lo:
        lo=p
        if s==2:
            st=''.join(str(tape.get(i,0)) for i in range(lo,max(tape)+1))
            m=Q.match(st);ty='Q'
            if not m: m=P.match(st);ty='P'
            if m:
                a=len(m.group(1))//3;b=len(m.group(2))//3;kk=len(m.group(3))
                cur=(ty,a,b,kk)
            else: cur=('X',st[:80])
            # print when not continuing pattern
            if prev and cur[0]==prev[0] and cur[0]!='X' and cur[1]==prev[1]+2 and cur[2]==prev[2]-1 and cur[3]==prev[3]:
                pass
            else:
                print(k+1,prev,'->',cur)
            prev=cur
