lines=open('gen35.py').read().split('\n')
out=[];i=0
while i<len(lines):
    l=lines[i]
    if l.strip().startswith("body = 'Lemma %s : %s.") and not l.rstrip().endswith("'") and i+4<len(lines) and lines[i+1]=='Proof.':
        out.append("            body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt) + wrap(tac) + 'Qed.\n'")
        i+=4
        continue
    out.append(l); i+=1
open('gen35.py','w').write('\n'.join(out))
