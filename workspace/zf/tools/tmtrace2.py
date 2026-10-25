"""Dispatch-level trace: path bits, trailing-ones count, register file decoded (selector marked with *)."""
import sys, re
sys.path.insert(0, 'tools')
from tmsim import load
def decode_rf(rf):
    # rf: register file string starting at first 1; registers = runs of 1s separated by single 0; '00' marks selector before the next register
    out=[]; sel=None
    runs=re.split(r'(0+)', rf.strip('0'))
    i=0; regs=[]
    for tok in runs:
        if not tok: continue
        if tok[0]=='1': regs.append(len(tok))
        else:
            if len(tok)==2: sel=len(regs)
            elif len(tok)>2: sel=('?',len(tok),len(regs))
    return regs, sel
def run(path, maxsteps, maxdisp, skip=0, nreg=14):
    start,tbl=load(path); tape={}; pos=0; st=start; steps=0; d=0
    while steps<maxsteps:
        if st=='main().0':
            d+=1
            if d>skip:
                hi=max(tape)
                ip=''.join(tape.get(i,'0') for i in range(pos, hi+1))
                j=ip.find('000'); ipb=ip[:j].rstrip('0'); rf=ip[j:].lstrip('0')
                m=re.match(r'([01]*?)(1*)$', ipb); prefix, ones = m.group(1), len(m.group(2))
                regs, sel = decode_rf(rf)
                tail=regs[-nreg:]; off=len(regs)-nreg
                shown=[]
                for k,v in enumerate(tail):
                    idx=off+k
                    shown.append(('*' if sel==idx else '')+str(v-1))
                print(f"{steps:9d} path={prefix:14s} ones={ones:2d} nregs={len(regs)} sel={sel} regs(last{nreg})={' '.join(shown)}")
            if d>=skip+maxdisp: return
        t=tbl.get((st,tape.get(pos,'0')))
        if t is None: print(f"HALT at step {steps} state {st}"); return
        w,dd,n=t; tape[pos]=w; pos+= 1 if dd=='R' else -1; st=n; steps+=1
if __name__=='__main__':
    run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv)>4 else 0)
