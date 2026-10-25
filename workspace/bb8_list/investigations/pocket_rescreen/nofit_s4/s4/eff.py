import subprocess, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen'); import idle
U=r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s2\use.exe'
rows=[l.rstrip('\n').split('\t') for l in open('machines.txt') if l.strip()]
groups={}
with open('eff.txt','w') as f:
  for fam,m in rows:
    o=subprocess.run([U,m,'30000000'],capture_output=True,text=True).stdout.split()
    used={x.split(':')[0]:x.split(':')[1] for x in o}
    tr=m.split('_'); e=[]
    for i,t in enumerate(tr):
        q=chr(65+i)
        e.append(''.join(t[3*b:3*b+3] if used[q+str(b)]!='-' else '...' for b in range(2)))
    em='_'.join(e); groups.setdefault(em,[]).append((fam,m)); f.write(f"{fam}\t{m}\t{em}\n")
for k,(em,v) in enumerate(sorted(groups.items(), key=lambda x:-len(x[1]))):
    print(f"E{k}", len(v), em, ' '.join(sorted(set(x[0] for x in v))))
