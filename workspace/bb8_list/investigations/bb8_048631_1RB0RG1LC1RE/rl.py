import rules,sys
ds,a,b=(),1,0
n=0
while n<int(sys.argv[1]):
    kd,r=rules.step(ds,a,b)
    if kd=='R4' or (kd=='R3' and rules.tz(ds)>=b-1 and n<10**6): print(n,kd,ds,a,b)
    ds,a,b=r; n+=1
