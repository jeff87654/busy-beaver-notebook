import sys
from tmlit import Sim, ST
TM='1RB0RG_1LC1RE_1LD0LD_0RA1LC_0RF0LC_1LG1RH_1LB1RG_1RF---'
def mk(word, off=0, state='A', size=1<<10):
    s=Sim.from_word(TM, word, off, state, size)
    return s
def show(s, lo=None, hi=None):
    lo = s.lo if lo is None else lo; hi = s.hi if hi is None else hi
    lo=min(lo,s.pos); hi=max(hi,s.pos)
    t=''.join(str(s.tape[i]) for i in range(lo,hi+1))
    p=s.pos-lo
    return t[:p]+'['+ST[s.state]+']'+t[p:]
if __name__=='__main__':
    word=sys.argv[1]; n=int(sys.argv[2])
    s=mk(word, 0, 'A')
    base=s.pos
    print(0, show(s,base-3,base+len(word)+3))
    for i in range(n):
        if not s.step(): print('HALT'); break
        print(s.steps, show(s,base-3,base+len(word)+3))
