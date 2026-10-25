from val import *
m0='1RB---_0RC0LA_1RD1LE_1LB0RF_1LC0RE_1RG1RE_1LH1RH_0LD0LG'
m='_'.join(''.join(t[i:i+3].replace('L','x').replace('R','L').replace('x','R') for i in (0,3)) for t in m0.split('_'))
def br(R):
    # stop at first event with 2 A-blocks whose config differs from bouncer continuation: emulate by stepping until y-phase start
    return bounce_round(m,'G',R,'01','01',pre='',mid='0',maxev=3000)
bad=n=0
X=lambda y,c: '0101'+'0'+'01'*y+('0'+'01'*c if c>0 else '')
for y in list(range(2,40))+[100,257]:
    for c in (2,4,6,10,20):
        n+=1; got=br(X(y,c)); exp=(2,2*y+4,'0'+'01'*(c-2) if c>2 else '')
        if got!=exp:
            bad+=1; print('MISMATCH',y,c,str(got)[:80])
    n+=1; got=br(X(y,0)); exp=(2,4,'0'+'01'*(2*y+2))
    if got!=exp: bad+=1; print('MISMATCH0',y,str(got)[:80])
print(n,'cases',bad,'bad')
