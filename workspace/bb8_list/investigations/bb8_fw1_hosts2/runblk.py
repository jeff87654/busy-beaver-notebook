import idle, subprocess, os, sys, time
from fam import BASES
HERE=os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE,'blk'),exist_ok=True)
for mode in ('7','8'):
    for nm in BASES:
        of=os.path.join(HERE,'blk','%s.m%s'%(nm,mode))
        if os.path.exists(of) and '# halt' in open(of).read(): continue
        t=time.time()
        with open(of,'w') as fo:
            p=subprocess.Popen([os.path.join(HERE,'blk.exe'),BASES[nm][0],mode,'1000000','100000'],stdout=fo,creationflags=0x40)
            with open(os.path.join(HERE,'pids.txt'),'a') as fp: fp.write('%d blk.exe %s m%s\n'%(p.pid,nm,mode))
            p.wait()
        print(nm,mode,'%.0fs'%(time.time()-t),open(of).read().strip().split('\n')[-1],flush=True)
