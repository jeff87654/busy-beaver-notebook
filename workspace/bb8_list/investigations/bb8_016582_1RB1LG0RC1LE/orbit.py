import sys
J=int(sys.argv[1]) if len(sys.argv)>1 else 3000
k=2; d=None   # d=None: exact
level=0
def f_t(t,M): # (8*4^t-5)/3 mod M/3 given t; M=3^(d)
    return ((8*pow(4,t,M)-5)//3) % (M//3)
while True:
    if d is None:
        m0=3+4*k; t,r=divmod(m0,3)
        print("level",level,"exact k bits",k.bit_length(),"r",r,"t bits",t.bit_length())
        if r==1: print("HALT at level",level);break
        if t>2000000:
            d=J; M=3**d
            kp=f_t(t,M); d-=1
            k=kp if r==0 else (4*kp+8)%3**d
            d=d; level+=1; continue
        kp=(8*4**t-5)//3
        k=kp if r==0 else 4*kp+8
        level+=1
    else:
        M=3**d
        m0=(3+4*k)%M; r=m0%3
        t=m0//3  # known mod 3^(d-1)
        print("level",level,"d",d,"r",r)
        if r==1: print("HALT at level",level);break
        if d<3: print("out of info");break
        kp=f_t(t,M); d-=1
        k=kp if r==0 else (4*kp+8)%3**d
        level+=1
