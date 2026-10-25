# vsr.py M Q pre X mid Y suf rulename : validate 2-param macro via cyc
import sys,subprocess,random
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
EXE=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s3\cyc.exe'
def run(M,Q,pre,X,mid,Y,suf,cases,rule,N=10**9,show=5):
    inp=''.join('%d %d\n'%c for c in cases)
    out=subprocess.run([EXE,M,Q,pre,X,mid,Y,suf,str(N)],input=inp,capture_output=True,text=True).stdout.strip().split('\n')
    bad=0
    for c,l in zip(cases,out):
        t=l.split('->')[1].split()
        got=(int(t[0]),int(t[1])) if t[0] not in ('HALT','TIMEOUT','TAPE') else t[0]
        if got!=rule(*c):
            bad+=1
            if bad<=show: print('BAD',l,'exp',rule(*c))
    print(M,len(cases),'cases',bad,'bad'); return bad
