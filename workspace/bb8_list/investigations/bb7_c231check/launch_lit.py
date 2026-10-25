import idle, subprocess, sys, os
os.environ['PATH']=r'C:\msys64\ucrt64\bin;'+os.environ['PATH']
here=os.path.dirname(os.path.abspath(__file__))
M={'1':"1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB",'2':"1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"}
for w in ('1','2'):
    with open(os.path.join(here,f'lit{w}.out'),'w') as f:
        p=subprocess.Popen([os.path.join(here,'lit.exe'),M[w],sys.argv[1]],stdout=f,creationflags=0x40)
        open(os.path.join(here,'pids.txt'),'a').write(f'{p.pid} lit.exe champ_23{w}\n')
        p.wait()
