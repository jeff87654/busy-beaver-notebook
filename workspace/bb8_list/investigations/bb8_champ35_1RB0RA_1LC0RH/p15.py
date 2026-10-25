from kk import *
def R(v,blk=(1,0)): return ('run',tuple(blk),lin({v:1}))
Z=(1,0,1)
t=3
cfg=('B',[1,0,1]*t+[0,1,BLANK],[0,1,0,1,1,0,0,1,0,0,1,0,0,1,0,1,0,BLANK],'<')
print(show(cfg))
for i in range(80):
    cfg=step(cfg)
    q=cfg[0]
    print(i+1,show(cfg)[:150])
