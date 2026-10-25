from cfg import *
def cellrun(left,right,target_pred,N=10**6):
    """left,right strings; head A on right[0]. run until state A and pred(word_left,word_right)."""
    L=[int(c) for c in left]; R=[int(c) for c in right]
    tape,p,q=build(L,R)
    for t in range(N):
        if t>0 and q==0:
            w=word(tape,p,q)
            l,r=w.split("[A]")
            r_=r.rstrip('0'); 
            if target_pred(l,r_): return t,l,r_
        r=tb[q*2+tape[p]]
        if r is None: return t,"HALT","ABCDEFGH"[q]+str(tape[p])
        tape[p]=r[0];p+=r[1];q=r[2]
    return None
def lit(left,right,expect_left,expect_right,N=10**6):
    """run until state A with exact left/right expected (left with leading zeros stripped; right rstrip 0)."""
    return cellrun(left,right,lambda l,r: l.lstrip('0')==expect_left.lstrip('0') and r==expect_right.rstrip('0'),N)
