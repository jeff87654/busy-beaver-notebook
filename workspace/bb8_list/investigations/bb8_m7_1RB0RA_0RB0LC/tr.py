import sys
M="1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE"
def parse(m):
    t={}
    for q,r in enumerate(m.split('_')):
        for c in range(2):
            x=r[3*c:3*c+3]
            t[(q,c)]=None if x=='---' else (int(x[0]),1 if x[1]=='R' else -1,ord(x[2])-65)
    return t
def rle(tp,lo,hi):
    s=''.join(map(str,tp[lo:hi+1]))
    out=[];i=0;n=len(s)
    while i<n:
        # pair runs
        if i+3<n and s[i]!=s[i+1] and s[i+2]==s[i] and s[i+3]==s[i+1]:
            j=i
            while j+1<n and s[j]==s[i] and s[j+1]==s[i+1]: j+=2
            out.append("(%s)^%d"%(s[i:i+2],(j-i)//2)); i=j; continue
        j=i
        while j<n and s[j]==s[i]: j+=1
        if j-i>=4: out.append("%s^%d"%(s[i],j-i))
        else: out.append(s[i:j])
        i=j
    return ' '.join(out)
def run(m,word,head,q,maxs,show=None,every=None):
    t=parse(m); SZ=1<<22; tp=[0]*SZ; off=SZ//2
    for i,ch in enumerate(word): tp[off+i]=int(ch)
    p=off+head; lo=off; hi=off+len(word)-1
    for st in range(maxs):
        c=tp[p]; tr=t[(q,c)]
        if tr is None:
            print("HALT",st,chr(65+q),p-off); return
        tp[p]=tr[0]; p+=tr[1]; q=tr[2]
        lo=min(lo,p); hi=max(hi,p)
        if show and show(st+1,q,p,tp,lo,hi):
            print(st+1,chr(65+q),p-off,rle(tp,lo,hi))
if __name__=='__main__':
    word=sys.argv[1]; maxs=int(sys.argv[2])
    def show(st,q,p,tp,lo,hi):
        return q==1 and p>=hi and tp[p]==0 and tp[hi]==0
    run(M,word,len(word),0+1,maxs,show)
