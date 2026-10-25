import idle, subprocess, os, sys, time
from fam import BASES
HERE=os.path.dirname(os.path.abspath(__file__))
PAIRS={'B1':['A10','B00'],'B2':['C10','D00'],'B3':['A10','G00'],'B4':['C10','G00'],
 'C1':['B00','E00','G10'],'C2':['D00','F00','G10'],'C3':['D00','F00','G10'],'C4':['C00','F00','G10'],'C5':['A10','C00','E00'],
 'C6':['C00','E00','G10'],'C7':['B00','D00','G10'],'C8':['A10','B00','D00'],'C9':['B00','D00','G10'],'C10':['A00','B00','B10','G10']}
for nm,ps in PAIRS.items():
    m,O,Q,f=BASES[nm]
    for pr in ps:
        of=os.path.join(HERE,'out','%s.m9_%s'%(nm,pr))
        with open(of,'w') as fo:
            p=subprocess.Popen([os.path.join(HERE,'scr.exe'),m,O,Q,f,os.path.join(HERE,'bat',nm+'.eng'),os.path.join(HERE,'bat',nm+'.rare'),'9',pr[:2],pr[2]],stdout=fo,creationflags=0x40)
            with open(os.path.join(HERE,'pids.txt'),'a') as fp: fp.write('%d scr.exe %s m9 %s\n'%(p.pid,nm,pr))
            p.wait()
        print(nm,pr,open(of).read().split('# total')[1].split('\n')[0] if '# total' in open(of).read() else 'FAILED',flush=True)
