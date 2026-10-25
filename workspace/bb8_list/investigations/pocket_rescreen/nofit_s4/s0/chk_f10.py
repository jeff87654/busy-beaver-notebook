from chk_round import run
M='1RB1LE_0RC1LG_0LD0LA_0RE1LA_0RF1LH_1RC0RF_1LD0LG_1LB---'
run(M,'L:E','E','0 1^3 0 1^3 0^3 1^3 0^3 1110^%d 0 011101^%%d 0',0,r'\[E\]0 \(1\)\^3 0 \(1\)\^3 \(0\)\^3 \(1\)\^3 \(0\)\^3 \(1110\)\^(\d+) 0 \(011101\)\^\d+ 0',[],None)
import chk_round
ok=bad=0
for k in range(3,103):
    r=chk_round.nxt(M,'L:E','E','0 1^3 0 1^3 0^3 1^3 0^3 1110^%d 0 011101^%d 0'%(k,k),0,r'\[E\]0 \(1\)\^3 0 \(1\)\^3 \(0\)\^3 \(1\)\^3 \(0\)\^3 \(1110\)\^(\d+) 0 \(011101\)\^\1 0')
    if r==k+1: ok+=1
    else: bad+=1; print(k,r)
print('ok',ok,'bad',bad)
