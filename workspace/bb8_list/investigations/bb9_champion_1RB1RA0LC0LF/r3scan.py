import sys
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M='1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
for y in (1,2,3):
  print('y+1=',y)
  for b in range(0,11):
    row=[]
    for k in range(1,14):
        r=run_next(M,(1,y)+(0,)*k,0,b)
        if r[0]=='K': row.append(show(r[2])[2:])
        else: row.append(r[0]+str(r[1]))
    print('b=%d'%b)
    for k,x in enumerate(row,1): print('   k=%d %s'%(k,x))
