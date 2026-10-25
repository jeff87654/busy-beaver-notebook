"""Literal (unaccelerated) check of the phase rules from event to next left-edge C event, with exact tape comparison."""
from rules import run, build
D='100'
def P(a,b,k): return '0'+D*a+'10'+D*b+'1'*k
def Q(a,b,j): return '0'+D*a+'10'+D*b+'101'+'1'*j
def X(a,m): return '0'+D*a+'1'*m
RULES=[]
# name, start, expected, steps formula
bad=0;cnt=0
def chk(name,st,exp,steps=None):
    global bad,cnt
    n,res,_=run(st)
    cnt+=1
    if res!=exp or (steps is not None and n!=steps):
        bad+=1;print('FAIL',name,st[:40],n,steps)
for a in range(0,25):
  for k in range(0,8):
    for b in range(0,6):
      chk('P1',P(a,b+1,k+1),P(a+2,b,k+1),6*a+21)
      chk('Q1',Q(a,b+1,k),Q(a+2,b,k),6*a+21)
    chk('P2',P(a,0,k+3),Q(1,a,k),6*a+23)
    chk('Q2',Q(a,0,k),X(a+2,k+1),6*a+12)
  for m in range(0,8):
    chk('X1',X(a,m+6),P(1,a,m+4),6*a+17)
  chk('X0',X(a+1,2),P(1,a+1,0),6*a+23)
  for b in range(0,6):
    chk('P0',P(a,b+2,0),P(a+2,b+1,0),6*a+21)
  chk('R0',P(a+1,1,0),P(1,0,3*a+8),6*a+36)
print('cases',cnt,'failures',bad)
# cycle and reset
def chain(st,target,limit=100000):
    cur=st
    for _ in range(limit):
        n,cur,res=run(cur)
        if cur==target: return True
        if cur is None: return False
    return False
def cyc(a,m):
    global bad,cnt
    cnt+=1
    if not chain(P(a,0,4*m+8),P(4*a+7,0,4*m+4)): bad+=1;print('FAIL Cyc',a,m)
for a in range(1,10):
  for m in range(0,4): cyc(a,m)
def g(a,m):
    for _ in range(m): a=4*a+7
    return a
for a in range(1,10):
  for m in range(0,3): 
    # Sup: P(a,0,4m+4) -> ... -> P(1,0,12 g + 20) reached as the first event after the m+1 phases (checked by chaining)
    cur=P(a,0,4*m+4)
    for _ in range(100000):
        n,cur2,res=run(cur)
        cur=cur2
        if cur==P(1,0,12*g(a,m)+20): break
    else: bad+=1;print('FAIL Sup',a,m)
print('cases',cnt,'failures',bad)
