import idle, subprocess, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
EXE=os.path.join(HERE,'rl.exe')
def rl(m,O,Q,runs,N=10**7,maxout=5,mode=0):
    inp=' '.join(map(str,runs)) if runs!='B' else 'B'
    p=subprocess.Popen([EXE,m,O,Q,str(N),str(maxout),str(mode)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'pids.txt'),'a') as f: f.write('%d rl.exe\n'%p.pid)
    out,_=p.communicate(inp)
    return out.strip().split('\n')
if __name__=='__main__':
    m,O,Q=sys.argv[1:4]; N=int(sys.argv[4]); mo=int(sys.argv[5]); mode=int(sys.argv[6])
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        r='B' if line=='B' else list(map(int,line.split()))
        print('>>',line)
        for l in rl(m,O,Q,r,N,mo,mode): print('   ',l)
