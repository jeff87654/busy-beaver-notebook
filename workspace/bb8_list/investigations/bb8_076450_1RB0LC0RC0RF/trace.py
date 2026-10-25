from lit import Sim
import sys
word = sys.argv[1]; state = sys.argv[2] if len(sys.argv)>2 else 'D'
nmax = int(sys.argv[3]) if len(sys.argv)>3 else 400
s = Sim(size=1<<12)
base = s.pos
for i,ch in enumerate(word): s.tape[base+i] = int(ch)
s.pos = base+len(word)+2; s.lo = base-1; s.hi = s.pos
s.state = 'ABCDEFGH'.index(state)
for i in range(nmax):
    t = s.tape
    print('%4d %s%s%s' % (s.steps, ''.join(map(str,t[base-3:s.pos])), '[%s%d]'%('ABCDEFGH'[s.state], t[s.pos]), ''.join(map(str,t[s.pos+1:s.hi+3]))))
    if not s.step(): print('HALT'); break
    if s.state==3 and s.tape[s.pos]==0 and s.pos>=s.hi and s.tape[s.pos-1]==0 and s.tape[s.pos-2]==0: 
        t = s.tape
        print('%4d %s%s' % (s.steps, ''.join(map(str,t[base-3:s.pos])), '[%s%d]'%('ABCDEFGH'[s.state], t[s.pos]))); break
