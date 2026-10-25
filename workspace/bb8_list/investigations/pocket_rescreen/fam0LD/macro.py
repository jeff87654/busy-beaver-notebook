import sys
from rules import pred
def run(L,maxrounds=10,verbose=True):
    rounds=0
    while True:
        if len(L)>=2 and L[1]>=1: L=[L[0]+2*L[1],0]+L[2:]; continue
        if len(L)==1:
            if verbose: print('single [c]: c=%d (c mod 3=%d, %d digits)'%(L[0],L[0]%3,len(str(L[0]))))
            rounds+=1
            if rounds>maxrounds: return ('rounds',L[0])
            if len(str(L[0]))>7 and L[0]%3!=1: return ('huge',L[0])
        p=pred(L)
        if p=='H': return ('H',L[0])
        L=p
if __name__=='__main__':
    print(run([int(x) for x in sys.argv[1:]]))
