from lit import Sim, compress
import sys
def run_from(word, maxsteps=10**7, nev=1):
    s = Sim(size=1<<16)
    base = s.pos
    for i,ch in enumerate(word):
        s.tape[base+i] = int(ch)
    s.pos = base+len(word)+2
    s.lo = base; s.hi = s.pos
    s.state = 3
    res = []
    st0 = s.steps
    while s.steps < maxsteps:
        if not s.step():
            return 'HALT after %d steps, ones=%d, tape=%s' % (s.steps, s.ones(), s.show())
        if s.state == 3 and s.pos >= s.hi and s.tape[s.pos]==0 and s.tape[s.pos-1]==0 and s.tape[s.pos-2]==0:
            lo = s.lo
            while s.tape[lo]==0: lo+=1
            W = ''.join(map(str, s.tape[lo:s.pos-2]))
            res.append((s.steps, W))
            if len(res) >= nev: break
    return res
if __name__ == '__main__':
    for M in range(0, 40):
        r = run_from('1'*M)
        if isinstance(r,str): print(M, r); continue
        st, W = r[0]
        print(M, st, compress(W))
