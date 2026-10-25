# shapes.py M STEPS SIDE[:STATE] [MAXLINES] [init_state hidx spec]: print records whose shape (exponents>=T -> n) changes
import sys,re,subprocess,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
TV=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tv.exe')
M,steps,side=sys.argv[1:4]; mx=int(sys.argv[4]) if len(sys.argv)>4 else 60
extra=sys.argv[5:8]
p=subprocess.Popen([TV,M,steps,side,'1','1','100000000']+extra,stdout=subprocess.PIPE,text=True)
prev=None; n=0; last=None
for l in p.stdout:
    if '|' not in l: print(l.strip()); continue
    cfg=l.split('|',1)[1].strip()
    sh=re.sub(r'\^(\d+)',lambda m:'^n' if int(m.group(1))>=6 else m.group(0),cfg)
    if sh!=prev:
        if last and last!=l: print('   ..',last.strip()[:230])
        print(l.strip()[:230]); n+=1; prev=sh
        if n>=mx: p.kill(); break
        last=None
    else: last=l
