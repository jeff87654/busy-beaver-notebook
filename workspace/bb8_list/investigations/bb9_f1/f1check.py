# F1 non-halting: static invariant check + literal simulation check.
# Invariant Inv: state C => cell left of head is 1;  state D => (head cell is 1) or (cell right of head is 1).
# Then E is entered only via D0 (0RE) whose target cell is 1, so E never reads 0.
import sys
BASE="1RB1RA_1LI1RC_0LD1LG_0RE1LD_---1RF_0LI0RA_1RA0LH_1LG1LH_{}0LF"
PAIRS=[("1LA","B"),("1LG","A"),("1LG","B"),("1LH","B"),("1LH","G"),("1RA","A")]
def parse(s):
    T={}
    for i,blk in enumerate(s.split("_")):
        st="ABCDEFGHI"[i]
        for r in (0,1):
            t=blk[3*r:3*r+3]
            T[(st,r)]=None if t[0]=="-" else (int(t[0]),1 if t[1]=="R" else -1,t[2])
    return T
def static(T):
    # every transition entering C writes 1 and moves R (so left of C-head is that 1)
    for (s,r),t in T.items():
        if t and t[2]=="C": assert t[0]==1 and t[1]==1,(s,r,t)
    # entering D: from C (reading 0, so left cell is 1 by Inv(C) -> new head cell is 1),
    # or from D1 (writes 1 moving L -> right cell 1). Any other entry would break Inv(D).
    for (s,r),t in T.items():
        if t and t[2]=="D":
            assert (s=="C" and t[1]==-1) or (s=="D" and r==1 and t[0]==1 and t[1]==-1),(s,r,t)
    # entering E: only from D reading 0 moving R (head cell 0 => by Inv(D) right cell is 1)
    for (s,r),t in T.items():
        if t and t[2]=="E": assert s=="D" and r==0 and t[1]==1,(s,r,t)
    return True
def sim(T,start,N):
    tape=bytearray(2*N+3); p=N+1; s=start
    for k in range(N):
        if s=="C": assert tape[p-1]==1
        elif s=="D": assert tape[p]==1 or tape[p+1]==1
        r=tape[p]; t=T[(s,r)]
        if t is None: return ("HALT",k)
        tape[p]=t[0]; p+=t[1]; s=t[2]
    return ("ok",N,sum(tape))
N=int(sys.argv[1]) if len(sys.argv)>1 else 10**6
for x,st in PAIRS:
    m=BASE.format(x); T=parse(m)
    assert st not in "CDE"
    print(m,st,"static",static(T),"sim",sim(T,st,N))
