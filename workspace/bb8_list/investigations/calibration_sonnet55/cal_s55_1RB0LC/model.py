# exact digit-list model of the machine (conjectured rules, checked vs literal in check_model.py)
# state: runs = list of [digit, count] bottom..top (top last); y >= 1
import sys
def pushrun(runs,d,k):
    if k<=0: return
    if runs and runs[-1][0]==d: runs[-1][1]+=k
    else: runs.append([d,k])
def step(runs,y):
    """one transfer+rule. returns (runs,y,event) event in 'pop','r0','r2', or ('HALT',...)"""
    runs=[r[:] for r in runs]
    if not runs: d=0
    else:
        top=runs[-1]
        if top[0]==1 and top[1]>1 and y%3==1:   # collapse pops of 1s
            k=top[1]; runs.pop(); return runs,y+6*k,'popk'
        d=top[0]; top[1]-=1
        if top[1]==0: runs.pop()
    c=d+y-1
    r=c%3
    if r==1: return runs,c+6,'pop'
    # e = last digit of P
    if runs:
        e=runs[-1][0]
    else: e=None
    if r==0:
        assert c>=3
        if e is None: pushrun(runs,2,1)
        else:
            runs[-1][1]-=1
            if runs[-1][1]==0: runs.pop()
            pushrun(runs,e+2,1)
        j=c//6
        pushrun(runs,1,3*j+1)
        if c%6==3: pushrun(runs,3,1); pushrun(runs,1,1)
        return runs,4,'r0'
    # r==2 : need e odd, e mod 6 in {3,5}; e is consumed, e' -> e'+2 followed by 1^k,3 (k>=0; e=3 -> e'+4)
    if e is not None and e%6 not in (3,5): return runs,y,('HALT',e,c)
    def dec():
        runs[-1][1]-=1
        if runs[-1][1]==0: runs.pop()
    if e is None:
        pass
    else:
        dec()
        e2=runs[-1][0] if runs else None
        if e2 is not None: dec()
        if e==3: pushrun(runs,(e2 or 0)+4,1)
        else:
            pushrun(runs,(e2 or 0)+2,1)
            k=(e-5)//2 if e%6==3 else (e-3)//2
            pushrun(runs,1,k); pushrun(runs,3,1)
    if e is None: pushrun(runs,2,1)
    j=c//6
    pushrun(runs,1,3*j+3)
    if c%6==5: pushrun(runs,3,1); pushrun(runs,1,1)
    return runs,4,'r2'
def Y(n):
    return ([[0,1]] if False else []),n
if __name__=="__main__":
    n=int(sys.argv[1])
    runs,y=[],n
    for i in range(int(sys.argv[2])):
        runs,y,ev=step(runs,y)
        if not runs and ev in('pop',):
            print("Y(%d)"%y)
        if isinstance(ev,tuple): print(ev);break
