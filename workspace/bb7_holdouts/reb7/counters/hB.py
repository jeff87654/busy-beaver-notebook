import idle, random, sys
from thr import rlg
M,O,Q=sys.argv[1:4]; n=int(sys.argv[4])
random.seed(int(sys.argv[5]) if len(sys.argv)>5 else 3)
H=0
for it in range(n):
    # random tape in the language: tokens of u=10 runs separated by '0' or '1'
    L=random.randint(1,7)
    bits=''
    for j in range(L):
        bits+='10'*random.randint(0,6)
        bits+=random.choice('0001')
    bits+='10'*random.randint(0,9)  # y
    o=rlg(M,O,Q,'10','0','1','P:'+bits+' 0',2*10**6,1,3)
    # note: input "P:bits 0" -> rlg builds prefix then run 0 then S; adjust: we want exactly bits; use runs empty? 
    if o[0].startswith('H'): H+=1; print('HALT',bits,o[0])
print('halts',H,'of',n)
