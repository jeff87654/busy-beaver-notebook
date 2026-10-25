import sys
from tmlit import Sim, ST
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
def trace(word, off, state='A', n=80, tm=ACT):
    s = Sim.from_word(tm, '0'*6+word+'0'*30, 6+off, state)
    for i in range(n):
        base=s.pos
        t=''.join(map(str,s.tape[s.pos-6-0:s.pos+0]))
        lo=s.lo; hi=s.hi
        seg=''.join(map(str,s.tape[lo:hi+1]))
        print('%3d %s %s'%(s.steps,ST[s.state],seg[:s.pos-lo]+'['+seg[s.pos-lo]+']'+seg[s.pos-lo+1:]))
        if not s.step(): print('HALT'); break
if __name__=='__main__':
    # word: A> 0 1^(b'+1) 0 1^(a+1) 0 ...; head at index 0
    trace(sys.argv[1], 0, sys.argv[2] if len(sys.argv)>2 else 'A', int(sys.argv[3]) if len(sys.argv)>3 else 80)
