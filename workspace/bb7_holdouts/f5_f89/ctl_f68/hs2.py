# exhaustive small token configs: A in 0..9, up to 4 digits in 0..3 with separators '.'/'#', end '#' -> count halts
import sys,subprocess,itertools
from mt import tape,KL
M=sys.argv[1]; steps=sys.argv[2] if len(sys.argv)>2 else '100000'
halts=[];n=0
seps=['.','#']
for A in range(0,8):
  for L in range(0,4):
    for ds in itertools.product(range(0,4),repeat=L):
      for ss in itertools.product(seps,repeat=L+1):
        tok=[str(A)] if A else []
        for i,d in enumerate(ds):
            tok.append(ss[i]);
            if d: tok.append(str(d))
        tok.append(ss[L]); 
        if ss[L]=='.': tok.append('#')
        t=' '.join(tok); n+=1
        p=subprocess.run([KL,M,steps,'D','L','a',tape(t)],capture_output=True,text=True)
        o=p.stdout.splitlines()
        if o and o[-1].startswith('HALT'): halts.append((t,o[-3:]))
for t,o in halts: print(t,' ||| ',' | '.join(x[:90] for x in o))
print(len(halts),'halts of',n)
