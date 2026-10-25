import idle, subprocess, random, sys
random.seed(int(sys.argv[1])); NC=int(sys.argv[2]); NK=sys.argv[3]
def odd(): return random.choice([1,1,1,1,3,3,5,7,9,11])
def even(): return random.choice([0,0,2,4,6,8])
def valid(S):
    if all(p%2==1 and q%2==1 for p,q in S): return 'O'
    if S[0][0]%2==0 and S[0][1]%2==1 and S[-1][0]%2==0 and S[-1][1]%2==1 and all(p%2==1 and q%2==1 for p,q in S[1:-1]) and len(S)>=2: return 'E'
    return None
starts=[]
for _ in range(NC):
    k=random.randint(1,6); ph=random.choice('OE')
    if ph=='E': k=max(k,2)
    S=[(odd(),odd()) for _ in range(k)]
    if ph=='E': S[0]=(even(),odd()); S[-1]=(even(),odd())
    for i in range(len(S)-1):
        if random.random()<0.4 and not(ph=='E' and i==0): S[i]=(1,1)
    starts.append(';'.join('%d,%d'%s for s in S))
out=subprocess.run(['./k2k.exe','20000000',NK],input='\n'.join(starts)+'\n',capture_output=True,text=True,creationflags=0x40).stdout
inv=0;halt=0;ok=0;nok=0
for l in out.split('\n'):
    if 'K step' in l:
        s=l.split(':')[1].strip()
        if 'IRREG' in s: print('IRREG',l); inv+=1; continue
        S=[tuple(map(int,x.split(','))) for x in s.split(';')]
        if valid(S) is None: print('INVALID', l); inv+=1
        else: ok+=1
    elif 'HALT' in l: halt+=1; print(l)
    elif 'NOK' in l or 'OUT' in l: nok+=1
print('ok',ok,'invalid',inv,'halt',halt,'nok',nok)
