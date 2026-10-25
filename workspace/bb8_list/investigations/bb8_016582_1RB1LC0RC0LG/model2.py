import sys; sys.set_int_max_str_digits(0)
"""Exact steps and sigma at halting, closed form for a level of j resets starting from C(L,7,3), L = 5j+a+1.
phase i (x_i = (32*4^i - 11)/3, y=3): n_i = (x_i-1)/2 rounds, cost n(4*3+64)+16n(n-1), then reset."""
def level_steps(j):
    """steps used by j phases i=0..j-1 (each = rounds + S6 reset) from C(L,7,3); returns (steps, x_j) and x_j"""
    tot=0
    # sums over i<j of n_i and n_i^2 with n_i=(16*4^i-7)/3
    S1=(4**j-1)//3; S2=(16**j-1)//15
    # sum n_i = (16*S1 - 7j)/3 ; sum n_i^2 = (256*S2 - 224*S1 + 49 j)/9
    sn=(16*S1-7*j)//3; sn2=(256*S2-224*S1+49*j)//9
    # per phase: 76 n + 16 n(n-1) + 6(8n+3) + 147  (S6 with y=8n+3)
    tot=76*sn+16*(sn2-sn)+6*(8*sn+3*j)+147*j
    x=(32*4**j-11)//3
    return tot,x
def run():
    t=130; L,x,y=1,7,3
    # level with L=1: rounds then S1
    while True:
        assert x==7 and y==3
        r=L%5
        j=(L-r-(1 if r==1 else 3 if r==3 else 4))//5 if r in (1,3,4) else None
        if r not in (1,3,4): raise Exception("bad residue L=%d"%L)
        a={1:0,3:2,4:3}[r]
        j=(L-a-1)//5
        tt,xj=level_steps(j)
        t+=tt
        n=(xj-1)//2
        t+=n*(4*3+64)+16*n*(n-1); y=8*n+3   # rounds down to x=1
        # note: level_steps included rounds+S6 for j phases; now the last rounds at L=a+1
        if r==4:
            return t+3*y+83,y+15
        if r==3: t+=4*y+198; L=y+9
        else: t+=4*y+204; L=y+11
        x,y=7,3
        print("next L=",L if L<10**7 else "big",file=__import__('sys').stderr)
if __name__=="__main__":
    steps,sigma=run()
    print("steps digits",len(str(steps)),"sigma digits",len(str(sigma)))
    print("steps=",str(steps)[:40],"...",str(steps)[-20:]);print("sigma=",str(sigma)[:40],"...",str(sigma)[-20:])
    open("result.txt","w").write("steps=%d\nsigma=%d\n"%(steps,sigma))
