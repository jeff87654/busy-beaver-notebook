# cmpp2.py PATHFILE [machine] [start_tape start_state]: check a tcps2 abstract path (newest first) against the real run
import sys,re
M=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='-' else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
tm={}
for i,r in enumerate(M.split('_')):
    for c in range(2):
        t=r[3*c:3*c+3]
        tm[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
L=open(sys.argv[1]).read().splitlines()
m=re.search(r'kL=(\d+) kR=(\d+) ML=(\d+) MR=(\d+)',L[0]); kL,kR,ML,MR=map(int,m.groups())
st=[]
for l in L:
    mm=re.match(r'\s+([A-H])(\d) \| L \[(\d*)\] (.*?) \| R \[(\d*)\] (.*)$',l)
    if mm: st.append(mm.groups())
st.reverse()
def tstate(cells,k,Mx):
    while cells and cells[-1]==0: cells=cells[:-1]
    if len(cells)<=Mx: return ''.join(map(str,cells))
    return ''.join(map(str,cells[:k]))+' ..? '+''.join(map(str,cells[-Mx:]))
def consistent(cells,u,s,k,Mx):
    u=[int(c) for c in u]
    if cells[:len(u)]!=u and not (len(cells)<len(u) and cells+[0]*(len(u)-len(cells))==u): return False
    rest=cells[len(u):]
    s=re.sub(r'^g[0-9a-f][0-9a-f] ','',s.strip())
    return tstate(rest,k,Mx)==s.replace('0^inf','').strip()
tape={}; p=0; q=0
for n,(aq,am,ul,sl,ur,sr) in enumerate(st):
    lo=min(list(tape)+[p])-60; hi=max(list(tape)+[p])+60
    left=[tape.get(i,0) for i in range(p-1,lo-1,-1)]; right=[tape.get(i,0) for i in range(p+1,hi+1)]
    ok=(q==ord(aq)-65 and tape.get(p,0)==int(am) and consistent(left,ul,sl,kL,ML) and consistent(right,ur,sr,kR,MR))
    if not ok:
        print('DIVERGE at abstract step',n)
        print('  abs : %s%s | L [%s] %s | R [%s] %s'%(aq,am,ul,sl,ur,sr))
        print('  real: %s%d | L %s | R %s'%(chr(65+q),tape.get(p,0),tstate(left,kL,ML),tstate(right,kR,MR)))
        lo=min(list(tape)+[p]); hi=max(list(tape)+[p])
        print('  real tape:',''.join(str(tape.get(i,0)) for i in range(lo,p)),'['+chr(65+q)+str(tape.get(p,0))+']',''.join(str(tape.get(i,0)) for i in range(p+1,hi+1)))
        break
    t=tm[(q,tape.get(p,0))]
    if t is None: print('real halt'); break
    tape[p]=t[0]; p+=t[1]; q=t[2]
else:
    print('path fully real')
