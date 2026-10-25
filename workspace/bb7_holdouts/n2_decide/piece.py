import idle, sys, re
from sim import T
# piece.py LEFTCELLS RIGHTCELLS state : run until state A with right = 00(11)^k or 01 ; print left/right
left=sys.argv[1]; right=sys.argv[2]; q='ABCDEFG'.index(sys.argv[3]) if len(sys.argv)>3 else 0
pad=40
tape={i:int(c) for i,c in enumerate('0'*pad+left+right)}; pos=pad+len(left)
for s in range(1,100000):
    b=tape.get(pos,0); tr=T[(q,b)]
    if tr is None: print('HALT',s); break
    tape[pos]=tr[0]; pos+=tr[1]; q=tr[2]
    hi=max(tape)+1
    r=''.join(str(tape.get(j,0)) for j in range(pos,hi+1)).rstrip('0')
    if q==0 and (re.fullmatch(r'00(?:11)*',r) or r=='01' or re.fullmatch(r'11(?:01)*00(?:11)*',r)):
        l=''.join(str(tape.get(j,0)) for j in range(min(tape),pos)).lstrip('0')
        print(s,'left=',l,'right=',r, 'minpos', min(k for k,v in tape.items() if v)-pad)
        if len(sys.argv)<5: break
