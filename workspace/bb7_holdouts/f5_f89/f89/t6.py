from msim import parse,M
import sys,re
T=parse(M)
digs=[int(x) for x in sys.argv[1].split(',')]
pat=sys.argv[3]
tape=list('000'+''.join('1'+'01'*d for d in digs)); h=0; q='D'
def rle(s):
    out=[];i=0
    while i<len(s):
        for w in ('01','1','0'):
            n=0
            while s.startswith(w,i): n+=1; i+=len(w)
            if n: out.append(w+('^%d'%n if n>1 else '')); break
    return ' '.join(out)
for st in range(int(sys.argv[2])):
    s=''.join(tape[:h])+'['+q+']'+''.join(tape[h:])
    if re.search(pat,s):
        print(st, rle(''.join(tape[:h])),'['+q+']',rle(''.join(tape[h:])))
    tr=T[(q,tape[h])]
    if tr is None: print('HALT'); break
    tape[h]=tr[0]; h+=tr[1]; q=tr[2]
    if h<0: tape.insert(0,'0'); h=0
    if h>=len(tape): tape.append('0')
