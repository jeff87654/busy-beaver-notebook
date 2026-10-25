from msim import parse,M
import sys
T=parse(M)
tape=list(sys.argv[1]); h=tape.index('['); q=tape[h+1]; del tape[h:h+3]
for st in range(int(sys.argv[2])):
    print(st, ''.join(tape[:h])+'['+q+']'+''.join(tape[h:]))
    tr=T[(q,tape[h])]
    if tr is None: print('HALT'); break
    tape[h]=tr[0]; h+=tr[1]; q=tr[2]
    if h<0: tape.insert(0,'0'); h=0
    if h>=len(tape): tape.append('0')
