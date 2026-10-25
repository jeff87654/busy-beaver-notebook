import idle, sys, subprocess, os
HERE=os.path.dirname(os.path.abspath(__file__))
def rlg(m,O,Q,u,s,S,inp,N=10**7,mo=1,mode=0):
    p=subprocess.Popen([os.path.join(HERE,'rlg.exe'),m,O,Q,u,s,S,str(N),str(mo),str(mode)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'pids.txt'),'a') as f: f.write('%d rlg.exe\n'%p.pid)
    out,_=p.communicate(inp); return out.strip().split('\n')
if __name__=='__main__':
    m,O,Q,u,s,S=sys.argv[1:7]; tops=eval(sys.argv[7]); acc=sys.argv[8] if len(sys.argv)>8 else 'odd'
    for top in tops:
      for k in range(1,6):
        for b in range(0,k+3):
          y=2*b+1 if acc=='odd' else 2*b
          r=top+[0]*k+[0,y]
          print(top,'k=%d b=%d'%(k,b),rlg(m,O,Q,u,s,S,' '.join(map(str,r)))[0])
