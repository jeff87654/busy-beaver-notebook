import re,sys,subprocess,os
only=sys.argv[1].split(',')
txt=open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs\zz_FamDev.v').read()
def adm(m):
    name=m.group(1)
    if name in only: return m.group(0)
    return 'Lemma %s : %s.\nProof. Admitted.\n'%(name,m.group(2))
txt=re.sub(r'Lemma (R3Am|R3Bm|R3Cm|R4m) : (.*?)\.\nProof\..*?\nQed\.\n',adm,txt,flags=re.S)
open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs\zz_FamDev2.v','w').write(txt)
os.chdir(r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs')
r=subprocess.run([r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe','-Q','../../third_party/busycoq/verify','BusyCoq','-Q','.','BB8','zz_FamDev2.v'],capture_output=True,text=True,timeout=300)
print((r.stdout+r.stderr)[:3000])
