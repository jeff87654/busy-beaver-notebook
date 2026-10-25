import itertools
F='1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE'
S=['1RB0LG_1LC0LE_1LF0LD_1RE0RB_1RB0RD_0LA---_1LA1LD','1RB0RD_1LC0LA_1LE0LD_1RA0RB_0LF---_1RB0LG_1LF1LD','1RB0RF_1RC0RE_0RD---_1LA0RG_1LF0LA_1LA0LE_1RD1RE']
def tab(m): 
    T={}
    for q,g in enumerate(m.split('_')):
        for s in range(2):
            t=g[3*s:3*s+3]; T[(q,s)]=None if t[2]=='-' else (int(t[0]),t[1],ord(t[2])-65)
    return T
def used(m,steps=200000):
    T=tab(m); tape={}; h=0; q=0; U=set()
    for _ in range(steps):
        s=tape.get(h,0); U.add((q,s)); tr=T[(q,s)]
        if tr is None: break
        tape[h]=tr[0]; h+=1 if tr[1]=='R' else -1; q=tr[2]
    return U
def traj(m,steps):
    T=tab(m); tape={}; h=0; q=0; out=[]
    for _ in range(steps):
        s=tape.get(h,0); tr=T[(q,s)]
        if tr is None: out.append('H'); break
        tape[h]=tr[0]; h+=1 if tr[1]=='R' else -1; q=tr[2]; out.append((h,tr[0]))
    return out
tf=traj(F,300000); tfm=[(-h,w) for h,w in tf]
for m in S:
    t=traj(m,300000)
    print(m,'same trajectory as F89' if t==tf else ('mirror trajectory' if t==tfm else 'DIFFERENT'))
    # state map along trajectory
    TF,TM=tab(F),tab(m)
    # simulate both, record state pairs
    def states(mm,steps=300000):
        T=tab(mm); tape={}; h=0; q=0; o=[]
        for _ in range(steps):
            s=tape.get(h,0); o.append((q,s)); tr=T[(q,s)]
            if tr is None: break
            tape[h]=tr[0]; h+=1 if tr[1]=='R' else -1; q=tr[2]
        return o
    pairs=set(zip([x[0] for x in states(F)],[x[0] for x in states(m)]))
    print('   state pairs (F89->sib):',sorted((chr(65+a),chr(65+b)) for a,b in pairs))
    print('   F89 unused transitions:',sorted((chr(65+q),s) for (q,s) in tab(F) if (q,s) not in used(F)), ' sib unused:',sorted((chr(65+q),s) for (q,s) in tab(m) if (q,s) not in used(m)))
