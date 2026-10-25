import idle, sys, subprocess
RK7=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'
def targs(t):
    f=t.split(','); d={}
    for x in f[2:]:
        k,v=x.split('=',1); d[k]=v
    al,be=d['d'].split('d+'); aB,bB=d['b'].split('b+')
    return [f[0],f[1],d['P'],d['u'],d['s'],al,be,aB,bB,d['S']]
if __name__=='__main__':
    m,t=sys.argv[1],sys.argv[2]; steps=sys.argv[3] if len(sys.argv)>3 else '100000000'; mk=sys.argv[4] if len(sys.argv)>4 else '400'
    out=subprocess.run([RK7,'trace',m]+targs(t)+[steps,mk],capture_output=True,text=True,creationflags=0x40).stdout
    prev=None
    for ln in out.splitlines():
        f=ln.split()
        if f[0]=='K':
            ds=f[2].split(',') if f[2]!='-' else []
            key=len(ds)
            # print when the list length changes or last-digit borrow
            if prev is None or key!=prev or len(sys.argv)>5:
                s=f[2] if len(f[2])<120 else f[2][:120]+'..'
                print(f[1],'n=%d'%len(ds),s,'a=',f[3],'b=',f[4])
            prev=key
        else: print(ln)
