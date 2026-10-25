# variant rules: 'a','b','c'
from rules import pred as pred_a
MS={'a':'1RB0LD_0RC---_1LC0RD_1LE1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG',
    'b':'1RB0LD_0RC---_1LC0RD_1LF1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG',
    'c':'1RB0LD_0RC---_1LC0RD_0RF1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG'}
def pred(L,v):
    if len(L)==1:
        c=L[0]
        if c%3==1: return 'H'
        k=c//3
        if c%3==2: return [2]+[1]*(2*k+1)+[0,0]
        if v=='a': return [2]+[1]*(2*k)+[0,0]
        if v=='b': return [0]+[1]*(2*k+1)+[0,0]
        if v=='c': return [0,0]+[1]*(2*k)+[0,0]
    if v=='c' and len(L)==3 and L[1]==0 and L[2]==0: return [L[0]+4]
    return pred_a(L)
