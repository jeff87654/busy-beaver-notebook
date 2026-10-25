"""d0read.py: from a c04raw --dv K line, parse the D0 moment into (s,y,P,L,t) if it is one:
   form (far->near) ... 1 (10)^(s+1) 1 (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001.  Reads the raw (non-dv) line."""
import sys, re
sys.path.insert(0,'.')
from rawparse import expand
def parse_d0(w):
    m = re.search(r'011(100)+', w)
    return None
for line in sys.stdin:
    if not line.startswith('K '): continue
    st = line.split()[1]
    body = line.split(' ',2)[2].split(' [')[0]
    w = expand(body)
    # match: 1 (10)^(s+1) 1 (10)^y 011 (100)^P then 1^L then 11 (11111100)^t 1001  (from the right/near)
    mm = re.search(r'1(10)+1(10)*011(100)+(1+)(00111111)*001001$', w.replace(' ',''))
    # simpler: find the "011(100)^P" block and counts around it
    ws = w.replace(' ','')
    m = re.search(r'011((?:100)+)(1+)11((?:11111100)*)1001$', ws)
    if m:
        P = len(m.group(1))//3; L = len(m.group(2)); t = len(m.group(3))//8
        pre = ws[:m.start()]
        # pre ends with ...1 (10)^(s+1) 1 (10)^y  -> parse last two (10)-runs
        g = re.search(r'1((?:10)+)1((?:10)*)$', pre)
        if g:
            s1 = len(g.group(1))//2; y = len(g.group(2))//2
            print(st, 's=%d y=%d P=%d L=%d t=%d'%(s1-1,y,P,L,t))
            continue
    # also catch the stop/cascade endpoint form
