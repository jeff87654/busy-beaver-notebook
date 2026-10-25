import sys
M="1RB1RD1LC_2LB1RB1LC_1RZ1LA1LD_0RB2RA2RD"
T={}
for qi,g in enumerate(M.split('_')):
    for s in range(3):
        t=g[3*s:3*s+3]
        T[(qi,s)]=(int(t[0]),1 if t[1]=='R' else -1, ord(t[2])-65)
def rle(cells):
    out=[];i=0
    while i<len(cells):
        j=i
        while j<len(cells) and cells[j]==cells[i]: j+=1
        out.append(f"{cells[i]}^{j-i}" if j-i>1 else f"{cells[i]}")
        i=j
    return ' '.join(out)
def run(maxsteps, show):
    tape={};pos=0;q=0;steps=0
    while steps<maxsteps:
        s=tape.get(pos,0)
        if show(q,s,pos,tape):
            lo=min(tape) if tape else 0; hi=max(tape) if tape else 0
            L=[tape.get(i,0) for i in range(lo,pos)]; R=[tape.get(i,0) for i in range(pos+1,hi+1)]
            print(steps, rle(L) if L else '', f"[{'ABCDZ'[q]}{s}]", rle(R) if R else '')
        w,d,nq=T[(q,s)]
        steps+=1
        if nq==25:
            tape[pos]=w; print("HALT",steps, sum(1 for v in tape.values() if v)); return
        tape[pos]=w;pos+=d;q=nq
    print("nohalt",steps)
if __name__=="__main__":
    n=int(sys.argv[1])
    run(n, lambda q,s,pos,tape: q==3 and s==1 and all(tape.get(i,0)!=2 for i in range(pos+1,max(tape)+1)))
