import sys,re,subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
SHP=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s2\shp.exe'
m,Q,S,steps,nmax=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
out=subprocess.run([SHP,m,steps,Q,S,'100000','A','-'],capture_output=True,text=True).stdout.split('\n')
last=None; n=0
for l in out:
    p=l.split(None,2)
    if len(p)<3: 
        if l.strip(): print(l.strip())
        continue
    s=p[2].strip(); k=re.sub(r'\^\d+','^#',s)
    k=re.sub(r'(0\(01\)\^# )+','L ',k)
    if k!=last: print(p[0], s[:160]); last=k; n+=1
    if n>=nmax: break
