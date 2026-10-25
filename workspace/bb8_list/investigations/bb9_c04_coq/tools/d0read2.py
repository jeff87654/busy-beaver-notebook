"""Parse a D0 cell-word (far side blank) into (far_prefix_cells, s, y, P, L, t). far given as token list far->near."""
import re, sys
sys.path.insert(0,'.')
from dtok import dtok, rle
def parse(ws):
    m = re.search(r'011((?:100)+)(1+)11((?:11111100)*)1001$', ws)
    if not m: return None
    P=len(m.group(1))//3; L=len(m.group(2)); t=len(m.group(3))//8
    pre=ws[:m.start()]
    g=re.search(r'1((?:10)+)1((?:10)*)$', pre)
    if not g: return None
    s=len(g.group(1))//2-1; y=len(g.group(2))//2
    far=pre[:g.start()+1]   # includes the leading 1 of the (10)^(s+1)? keep prefix up to g.start
    far=pre[:g.start()]
    return far, s, y, P, L, t
if __name__=='__main__':
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        r=parse(line)
        if r: far,s,y,P,L,t=r; print('s=%d y=%d P=%d L=%d t=%d far_dtok= %s'%(s,y,P,L,t, rle(dtok(far.lstrip('0')))))
        else: print('no parse')
