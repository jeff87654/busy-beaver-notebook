import sys,subprocess
KL=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\f5_f89\kl2.exe'
def tape(tok,lead='D000'):
    s=lead
    for t in tok.split():
        if t=='.': s+='0'
        elif t=='#': s+='1'
        elif '^' in t:  # (x .)^n written as x.^n
            x,n=t.split('^'); s+=('10'*int(x.rstrip('.'))+'0')*int(n)
        else: s+='10'*int(t)
    return s
def run(M,tok,steps,n=40,q='D',side='L'):
    p=subprocess.run([KL,M,str(steps),q,side,'a',tape(tok)],capture_output=True,text=True)
    return p.stdout.splitlines()[:n]
if __name__=='__main__':
    M=sys.argv[1]; steps=int(sys.argv[3]); n=int(sys.argv[4]) if len(sys.argv)>4 else 40
    for tok in sys.argv[2].split(';'):
        print('==',tok)
        for l in run(M,tok,steps,n): print('  ',l[:220])
