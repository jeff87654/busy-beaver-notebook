# cmpp.py PATHFILE [machine]: compare a tcps abstract path (printed newest first) with the real run from the blank tape
import sys,re
M=sys.argv[2] if len(sys.argv)>2 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RG0LC_1RG1LD_0RH0RF_---0RE'
tm={}
for i,r in enumerate(M.split('_')):
    for c in range(2):
        t=r[3*c:3*c+3]
        tm[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
L=open(sys.argv[1]).read().splitlines()
hdr=L[0]; m=re.search(r'kL=(\d+) kR=(\d+) ML=(\d+) MR=(\d+)',hdr); kL,kR,ML,MR=map(int,m.groups())
steps=[]
for l in L:
    mm=re.match(r'\s+([A-H])(\d) \| L (.*?) \| R (.*)$',l)
    if mm: steps.append((ord(mm.group(1))-65,int(mm.group(2)),mm.group(3).strip(),mm.group(4).strip()))
steps.reverse()
def absside(cells,k,Mx):
    # cells: list nearest first, trailing zeros trimmed
    while cells and cells[-1]==0: cells=cells[:-1]
    if len(cells)<=Mx: return ''.join(map(str,cells))+' 0^inf'
    return ''.join(map(str,cells[:k]))+' ..? '+''.join(map(str,cells[-Mx:]))+' 0^inf'
tape={}; p=0; q=0
for n,(aq,am,al,ar) in enumerate(steps):
    lo=min(list(tape)+[p]); hi=max(list(tape)+[p])
    left=[tape.get(i,0) for i in range(p-1,lo-1,-1)]; right=[tape.get(i,0) for i in range(p+1,hi+1)]
    rl=absside(left,kL,ML); rr=absside(right,kR,MR)
    ok=(q==aq and tape.get(p,0)==am and rl.strip()==al.strip() and rr.strip()==ar.strip())
    if not ok:
        print('DIVERGE at abstract step',n)
        print('  abs : %s%d | L %s | R %s'%(chr(65+aq),am,al,ar))
        print('  real: %s%d | L %s | R %s'%(chr(65+q),tape.get(p,0),rl,rr))
        print('  real tape:',''.join(str(tape.get(i,0)) for i in range(lo,hi+1)),'head at',p-lo)
        break
    t=tm[(q,tape.get(p,0))]
    if t is None: print('real halt'); break
    tape[p]=t[0]; p+=t[1]; q=t[2]
else:
    print('path fully real')
