from rules import step
from final4 import halt_run
bad=0;n=0
def chk(cfg,exp):
    global bad,n
    n+=1
    r=step(*cfg)
    if r is None or r[0]!=exp[0] or tuple(r[1])!=tuple(exp[1]):
        bad+=1;print("BAD",cfg,r,exp)
for l in range(1,9):
  for x in range(0,8):
    for y in range(1,14):
        chk((l,x+2,y),(4*y+64,(l,x,y+8)))
for l in range(0,7):
    for y in range(1,25): chk((l+6,1,y),(6*y+147,(l+1,y+12,3)))
for y in range(1,60):
    chk((3,1,y),(4*y+198,(y+9,7,3))); chk((1,1,y),(4*y+204,(y+11,7,3)))
    h=halt_run(4,1,y); n+=1
    if h[:3]!=(3*y+83,y+15,'G') or h[3]!=0: bad+=1;print("BAD4",y,h)
print(n,"cases",bad,"bad")
