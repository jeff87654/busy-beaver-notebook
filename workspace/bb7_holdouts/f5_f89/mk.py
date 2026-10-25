import sys,subprocess
KL=r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\f5_f89\kl.exe'
def tape(A,ds,tail='1',lead='D000'):
    return lead+'10'*A+'0'+''.join('10'*d+'0' for d in ds)+tail
def run(M,t,steps,q='D',side='L',mode='a',n=40):
    p=subprocess.run([KL,M,str(steps),q,side,mode,t],capture_output=True,text=True)
    return p.stdout.splitlines()[:n]
if __name__=='__main__':
    M=sys.argv[1]; A=int(sys.argv[2]); ds=eval(sys.argv[3]); steps=int(sys.argv[4]); n=int(sys.argv[5]) if len(sys.argv)>5 else 40
    for l in run(M,tape(A,ds),steps,n=n): print(l[:220])
