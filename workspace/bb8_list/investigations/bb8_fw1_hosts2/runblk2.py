import idle, subprocess, os, sys, time
from fam import BASES, SIB
HERE=os.path.dirname(os.path.abspath(__file__))
for mode in ('7','8'):
    for nm in SIB:
        of=os.path.join(HERE,'blk','%s.m%s'%(nm,mode))
        if os.path.exists(of) and '# halt' in open(of).read(): continue
        with open(of,'w') as fo:
            p=subprocess.Popen([os.path.join(HERE,'blk.exe'),BASES[nm][0],mode,'1000000','100000'],stdout=fo,creationflags=0x40)
            with open(os.path.join(HERE,'pids.txt'),'a') as fp: fp.write('%d blk.exe %s m%s\n'%(p.pid,nm,mode))
            p.wait()
        print(nm,mode,open(of).read().strip().split('\n')[-1],flush=True)
