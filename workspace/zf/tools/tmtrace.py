"""Trace Wade's machine: at each main().0 dispatch print the IP bits and the register file compactly."""
import sys
sys.path.insert(0, 'tools')
from tmsim import load
def run(path, maxsteps, maxdisp, skip=0):
    start,tbl=load(path); tape={}; pos=0; st=start; steps=0; d=0
    while steps<maxsteps:
        if st=='main().0':
            d+=1
            if d>skip:
                lo=min(tape); hi=max(tape)
                s=''.join(tape.get(i,'0') for i in range(lo,hi+1))
                # IP: from pos back to the marker 1, then registers after run of zeros
                ip=''.join(tape.get(i,'0') for i in range(pos, hi+1))
                # split: IP bits then >=3 zeros then register file
                j=ip.find('000'); ipb=ip[:j]; rf=ip[j:].lstrip('0')
                regs=[len(r) for r in rf.split('0')] if rf else []
                print(f"{steps:8d} ip={ipb:20s} regs={regs}")
            if d>=skip+maxdisp: return
        t=tbl.get((st,tape.get(pos,'0')))
        if t is None: print(f"HALT at step {steps} state {st}"); return
        w,dd,n=t; tape[pos]=w; pos+= 1 if dd=='R' else -1; st=n; steps+=1
if __name__=='__main__':
    run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv)>4 else 0)
