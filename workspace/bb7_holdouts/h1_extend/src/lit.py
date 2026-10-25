import sys
def parse(m):
    T={}
    for i,r in enumerate(m.split('_')):
        for c in range(2):
            t=r[3*c:3*c+3]
            T[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
    return T
def run(m,steps,show=()):
    T=parse(m); tape={}; p=0; q=0
    for s in range(steps+1):
        if s in show:
            lo=min(tape) if tape else 0; hi=max(tape) if tape else 0
            st=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
            print(s, 'ABCDEFGHI'[q], 'head@', p-lo, 'len', hi-lo+1); print(st)
        c=tape.get(p,0); tr=T[(q,c)]
        if tr is None: print('HALT',s); return
        tape[p]=tr[0]; p+=tr[1]; q=tr[2]
if __name__=='__main__':
    run(sys.argv[1],int(sys.argv[2]),set(int(x) for x in sys.argv[3].split(',')))
