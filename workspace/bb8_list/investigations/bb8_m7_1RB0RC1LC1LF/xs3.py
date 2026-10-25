import planner8 as pl
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
pl.set_tm(M)
for beh in ([1],[1,0],[1,0,1],[1,0,1,0,0,1,1,0],[0],[0,1,0]):
    print(beh, pl.derive_crossing('F','<',(1,1,0),beh))
