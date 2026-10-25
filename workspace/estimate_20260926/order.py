tm="1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF"
rows=tm.split('_'); T={}
for s,r in enumerate(rows):
    for c in range(2): T[(s,c)]=r[3*c:3*c+3]
tape={};pos=0;st=0;order=[];seen=set()
for step in range(200000):
    c=tape.get(pos,0)
    if (st,c) not in seen: seen.add((st,c)); order.append((st,c,step))
    t=T[(st,c)]
    if t[2]=='Z': break
    tape[pos]=int(t[0]); pos+= 1 if t[1]=='R' else -1; st=ord(t[2])-65
print([(chr(65+s)+str(c),k) for s,c,k in order])
# emit partial 8-state machines along the TNF path: first m transitions defined
import json
out=[]
for m in range(1,14):
    d={(s,c) for s,c,_ in order[:m]}
    parts=[]
    for s in range(8):
        g=''
        for c in range(2):
            g+= T[(s,c)] if (s,c) in d and s<7 else '---'
        parts.append(g)
    used_states={0}|{ord(T[(s,c)][2])-65 for (s,c) in d if T[(s,c)][2]!='Z'}
    mus=max(used_states)+1  # TNF: states used so far are a prefix A..
    muc=2
    out.append((m,'_'.join(parts),mus,muc,16-m))
for o in out: print(*o)
