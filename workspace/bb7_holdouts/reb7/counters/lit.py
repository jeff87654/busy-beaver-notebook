import idle, sys
# literal blank-tape sim; prints RLE tape at moments: state Q, head on blank, all 1s to the left (template orientation O)
def parse(m):
    rows=m.split('_'); T={}
    for i,r in enumerate(rows):
        for c in range(2):
            t=r[3*c:3*c+3]
            if t[2] in '-H' or t=='---': T[(i,c)]=None
            else: T[(i,c)]=(int(t[0]), 1 if t[1]=='R' else -1, ord(t[2])-65)
    return T
def run(m,O,Q,N,maxout=200,start=None):
    T=parse(m); s=-1 if O=='L' else 1
    tape={}; p=0; q=0; lo=hi=0; out=0
    for st in range(N):
        c=tape.get(p,0); tr=T[(q,c)]
        if tr is None:
            print('H',st,sum(tape.values())); return
        w,d,nq=tr; tape[p]=w
        if w: lo=min(lo,p); hi=max(hi,p)
        p+=d; q=nq
        if q==Q and tape.get(p,0)==0:
            # all ones on the template-left side?
            if s==1 and hi<p or s==-1 and lo>p:
                cells=[tape.get(i,0) for i in (range(lo,p) if s==1 else range(hi,p,-1))]
                # template order: left to right as in template (for L, mirrored: read from far end towards head)
                strg=''.join(map(str,cells)).lstrip('0')
                # rle
                o=[];i=0
                while i<len(strg):
                    j=i
                    while j<len(strg) and strg[j]==strg[i]: j+=1
                    o.append(strg[i]+('^%d'%(j-i) if j-i>1 else '')); i=j
                print('K',st+1,'.'.join(o)); out+=1
                if out>=maxout: return
    print('END',N)
if __name__=='__main__':
    run(sys.argv[1],sys.argv[2],ord(sys.argv[3])-65,int(sys.argv[4]),int(sys.argv[5]))
