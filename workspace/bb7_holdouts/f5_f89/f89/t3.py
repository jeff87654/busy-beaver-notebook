from msim import parse,M
import sys
T=parse(M)
digs=[int(x) for x in sys.argv[1].split(',')]
tape=list('000'+''.join('1'+'01'*d for d in digs)+'0'*6); h=0; q='D'; lo=0
for st in range(int(sys.argv[2])):
    s=''.join(tape[:h])+'['+q+']'+''.join(tape[h:])
    if st%int(sys.argv[3])==0 or True: print(st, s)
    tr=T[(q,tape[h])]
    if tr is None: print('HALT'); break
    tape[h]=tr[0]; h+=tr[1]; q=tr[2]
    if h<0: tape.insert(0,'0'); h=0
    if h>=len(tape): tape.append('0')
