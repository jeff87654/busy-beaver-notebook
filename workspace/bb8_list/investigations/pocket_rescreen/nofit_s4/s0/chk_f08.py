from chk_round import run
M='1RB1RG_0RC---_1LD0RC_0LE0LC_1RF0LC_0RA0RH_0RF1LC_0LA1RD'
run(M,'L:E','E','0 01^3 001 10^%d 01',0,r'\[E\]0 \(01\)\^3 0 0 1 \(10\)\^(\d+) 0 1',range(2,202,2),lambda n:4*n+4)
