from pathlib import Path
from collections import Counter
import json
from sim import parse
machine=Path('discovery_holdouts.txt').read_text().splitlines()[2]
T=parse(machine);tape=set();p=st=0;gaps=Counter();windows=Counter();boundaries=[];violations=[]
for step in range(2_000_000):
    r=int(p in tape)
    if st==5 and r:
        d=next((j for j in range(1,50) if p+j in tape),None)
        gaps[d]+=1
        windows[''.join(str(int(p+j in tape)) for j in range(-5,10))]+=1
        if d!=4 and len(violations)<20: violations.append([step,p,d])
        if not any(p-j in tape for j in range(1,4)) and len(boundaries)<100:
            lo=min(tape);hi=max(tape)
            boundaries.append({'step':step,'head':p,'left':' '.join(map(str, sorted(p-x for x in tape if x<p))), 'right_word':''.join(str(int(x in tape)) for x in range(p,hi+1))})
    w,d,st=T[st][r]
    if w:tape.add(p)
    else:tape.discard(p)
    p+=d
    if st<0: break
out={'steps':step+1,'gap_histogram':dict(gaps),'violations':violations,'window_histogram':windows,'boundary_events':boundaries}
Path('unresolved_c03_structure.json').write_text(json.dumps(out,indent=2))
print('gaps',gaps,'violations',violations,'windows',len(windows))
print('topwindows',windows.most_common(20))
print('boundaries',boundaries[:16])
