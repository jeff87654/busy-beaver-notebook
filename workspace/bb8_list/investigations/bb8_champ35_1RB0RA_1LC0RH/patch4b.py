L=open('gen35.py').read().split('\n')
new=["            body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt) + wrap(tac) + 'Qed.\n'"]
L=L[:179]+new+L[184:]
open('gen35.py','w').write('\n'.join(L))
