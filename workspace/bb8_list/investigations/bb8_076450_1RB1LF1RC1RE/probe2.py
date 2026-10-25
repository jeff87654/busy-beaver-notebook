# For a word w (followed by random tail r), run to next left-edge A0; report result word and max pos visited relative to w
import sys, random
from lit import parse, ST, MAIN
T = parse(MAIN)
def run(word, maxsteps=10**7):
    n = len(word); pad = 4*n+64
    tape = bytearray(pad)+bytearray(int(c) for c in word)+bytearray(pad)
    pos = pad-1; st=0; steps=0; maxpos=pos
    while True:
        e = T[st][tape[pos]]
        if e is None: return 'HALT', steps, None, maxpos-pad
        w,d,q = e; tape[pos]=w; pos+=d; st=q; steps+=1
        maxpos=max(maxpos,pos)
        if st==0 and tape[pos]==0 and not any(tape[:pos]):
            hi=len(tape)-1
            while hi>pos and tape[hi]==0: hi-=1
            return 'A0', steps, ''.join(map(str,tape[pos+1:hi+1])), maxpos-pad
        if steps>maxsteps: return 'LIMIT',steps,None,None
for w in sys.argv[1:]:
    w = eval(w)
    print(w, run(w))
