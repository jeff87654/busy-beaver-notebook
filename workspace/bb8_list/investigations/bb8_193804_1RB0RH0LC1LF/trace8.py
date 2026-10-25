import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
def blocks(bs): return ''.join('1'*b+'0' for b in bs)
W=[2,2,3,2,3]
def Wm(m): return [W[i%5] for i in range(m)]
A0=[1,2,3,2,3]; B0=[2,1,3]
def match(w):
    # w = tape cells left of head (head cell is the blank after last block)
    for name,pre in (('A',A0),('B',B0)):
        for m in range(0,400):
            if blocks(pre+Wm(m))==w: return name,m
    return None
if __name__=='__main__':
    s=Sim(TM,1<<20)
    a=int(sys.argv[1]); cnt=int(sys.argv[2])
    prev=0; n=0
    while n<cnt:
        s.step()
        if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
            gap=s.steps-prev; prev=s.steps
            if s.steps>a and gap>500:
                lo,hi=s.bounds()
                w=''.join(map(str,s.tape[lo:s.pos+1]))
                print(s.steps,gap,match(w), len(w)); n+=1
