from sim import *
import sys, re, collections
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); S=sys.argv[4]
cnt=collections.Counter(); ex={}
def rl(s):
    return ' '.join('%s^%d'%(m.group()[0],len(m.group())) for m in re.finditer(r'0+|1+',s))
def cb(i,tape,pos,s):
    if a<=i<b and s in S:
        lo=min(tape);hi=max(tape)
        L=''.join(str(tape.get(p,0)) for p in range(lo,pos)).lstrip('0')
        R=''.join(str(tape.get(p,0)) for p in range(pos,hi+1)).rstrip('0')
        key=re.sub(r'0{2,}','0+',L)+' | '+R[:8]
        cnt[key]+=1
        if key not in ex: ex[key]=(i,L,R)
run(N,cb)
for k,v in sorted(cnt.items(),key=lambda x:-x[1]): print(v,k,'   eg',ex[k][0],ex[k][1][-30:],'[]',ex[k][2][:30])
