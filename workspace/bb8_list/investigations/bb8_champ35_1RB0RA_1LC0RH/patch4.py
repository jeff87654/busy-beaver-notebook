L=open('gen35.py').read().split('\n')
# lines index 179..184 (0-based) correspond to file lines 180..185
new=["            body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt) + wrap(tac) + 'Qed.\n'"]
L=L[:179]+new+L[184:]
open('gen35.py','w').write('\n'.join(L))
