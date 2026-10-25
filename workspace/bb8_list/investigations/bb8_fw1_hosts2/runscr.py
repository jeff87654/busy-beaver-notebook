import idle, subprocess, sys, os, time
from fam import BASES
HERE=os.path.dirname(os.path.abspath(__file__))
mode=sys.argv[1]; names=sys.argv[2:] or list(BASES)
for nm in names:
    m,O,Q,f=BASES[nm]
    of=os.path.join(HERE,'out','%s.m%s'%(nm,mode))
    for attempt in range(4):
        t=time.time()
        with open(of,'w') as fo:
            from fam import filt
            p=subprocess.Popen([os.path.join(HERE,'scr.exe'),m,O,Q,filt(nm),os.path.join(HERE,'bat',nm+'.eng'),os.path.join(HERE,'bat',nm+'.rare'),mode],stdout=fo,creationflags=0x40)
            with open(os.path.join(HERE,'pids.txt'),'a') as fp: fp.write('%d scr.exe %s m%s\n'%(p.pid,nm,mode))
            rc=p.wait()
        txt=open(of).read()
        if '# total' in txt: break
        print(nm,mode,'attempt',attempt,'rc',rc,flush=True)
    print(nm,mode,'%.0fs'%(time.time()-t),txt.split('# total')[1].split('\n')[0] if '# total' in txt else 'FAILED',flush=True)
