"""Fast TM helpers on plain dict tables {(state,sym):(w,d,next)} with sym/w in '01'."""
import re
def load(path):
    start=None; tbl={}
    for l in open(path, encoding='utf-8'):
        l=l.strip()
        if l.startswith('#!'):
            p=l[2:].split()
            if p and p[0]=='start': start=p[1]
        elif l and not l.startswith('#'):
            s,r,w,d,n=l.split(); tbl[(s,r)]=(w,d,n)
    return start,tbl
def from_tm(t):
    return t.start, {k:(v.write,v.direction,v.nextstate) for k,v in t.states.items()}
def save(path, start, tbl, header=''):
    with open(path,'w') as f:
        f.write(f'#! start {start}\n')
        if header: f.write(''.join('# '+h+'\n' for h in header.splitlines()))
        for (s,r) in sorted(tbl): w,d,n=tbl[(s,r)]; f.write(f'{s} {r} {w} {d} {n}\n')
def nstates(tbl): return len({s for s,_ in tbl})
def run_until(tbl, start, target, maxsteps, tape=None, pos=0):
    """Run until state==target (returns tape,pos,steps) or None."""
    tape = {} if tape is None else tape; st=start; steps=0
    while steps<maxsteps:
        if st==target: return tape,pos,steps
        t=tbl.get((st,tape.get(pos,'0')))
        if t is None: return None
        w,d,n=t; tape[pos]=w; pos+= 1 if d=='R' else -1; st=n; steps+=1
    return None
def boot_check(tape, pos, nreg=11):
    """Check the post-boot dispatch tape: 0^inf 1 [head]0^g (1+0)*1+ 0^inf, last nreg runs = '1'.
    Returns (ok, gap, nruns, reason)."""
    lo=min(tape); hi=max(tape)
    if tape.get(pos-1,'0')!='1': return (False,0,0,'no marker')
    if any(tape.get(i,'0')=='1' for i in range(lo,pos-1)): return (False,0,0,'junk left of marker')
    g=0; i=pos
    while i<=hi and tape.get(i,'0')=='0': g+=1; i+=1
    s=''.join(tape.get(j,'0') for j in range(i,hi+1)).rstrip('0')
    if not s or g < 1: return (False,g,0,'no registers')
    if '00' in s: return (False,g,0,'00 in register file')
    runs=s.split('0')
    if len(runs)<nreg or any(r!='1' for r in runs[-nreg:]): return (False,g,len(runs),'regs not zero')
    return (True,g,len(runs),'ok')
