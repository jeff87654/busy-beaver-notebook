import sys,re,json
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1])
heads=[]
for step in range(n):
    s=tape.get(pos,0)
    if pos==-2 and q==7:
        hi=max(k for k,v in tape.items() if v)
        st=''.join(str(tape.get(i,0)) for i in range(0,hi+1))
        rl=[(len(a),len(b)) for a,b in re.findall('(1+)(0*)',st)]
        k=0
        while k<len(rl) and rl[k]==(1,1): k+=1
        rest=rl[k:]
        if rest and rest[0][0]==2 and k>=2 and rest[0][1]==2*k+3 and all(x==1 for x,y in rest[1:]) and all(y%2==1 for x,y in rest[1:-1]):
            ts=tuple((y+1)//2 for x,y in rest[1:-1])
            heads.append((step,k,ts,hi+1))
    w,d,nq=T[(q,s)]
    tape[pos]=w; pos+=1 if d=='R' else -1; q=nq
json.dump(heads,open('heads.json','w'))
print(len(heads))
