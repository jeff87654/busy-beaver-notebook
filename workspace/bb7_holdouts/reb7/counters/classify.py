import idle, subprocess, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
def run(args,inp=None):
    p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40,cwd=HERE)
    with open(os.path.join(HERE,'pids.txt'),'a') as f: f.write('%d %s\n'%(p.pid,os.path.basename(args[0]) if args[0]!=sys.executable else args[1]))
    out,_=p.communicate(inp); return out
N=sys.argv[2] if len(sys.argv)>2 else '500000000'
os.makedirs(os.path.join(HERE,'trd'),exist_ok=True)
for line in open(sys.argv[1]):
    m,O,Q=line.split()[:3]
    res=[]
    for S in ('0','-'):
        t=run([os.path.join(HERE,'rlg.exe'),m,O,Q,'1','0',S,N,'60','0'],'B')
        fn=os.path.join(HERE,'trd','%s_C%s.txt'%(m,S)); open(fn,'w').write(t)
        nl=t.count('|')//2
        for nt in ([],['5'],['3'],['7']):
            r=run([sys.executable,os.path.join(HERE,'trace_check.py'),'C',fn]+nt).strip().split('\n')[-1]
            res.append('C S=%s top=%s n=%d: %s'%(S,nt[0] if nt else '-',nl,r))
    for fam,SS in (('B','1'),('A','-')):
        t=run([sys.executable,os.path.join(HERE,'pb2.py'),m,O,Q,'60','4',N,SS],'B')
        fn=os.path.join(HERE,'trd','%s_%s.txt'%(m,fam)); open(fn,'w').write(t)
        nl=t.count(' : ')
        r=run([sys.executable,os.path.join(HERE,'trace_check.py'),fam,fn]).strip().split('\n')[-1]
        res.append('%s n=%d: %s'%(fam,nl,r))
    print(m,O,Q); [print('   ',x) for x in res]; sys.stdout.flush()
