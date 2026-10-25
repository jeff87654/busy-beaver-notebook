p='coqgen.py'
L=open(p).read().split('\n')
i=[k for k,l in enumerate(L) if l.startswith("    tac = ['induction j; intros.'")][0]
assert L[i+2].startswith("    text = helpers + 'Lemma")
L[i]="    first = ['follow (%s %s).' % (rname, ' '.join(rc + rv))] if ops is None else ops_to_tactics(ops)\n    tac = ['induction j; intros.', '- simpl. finish_norm.', '- simpl.'] + first + \\"
L[i+2]=L[i+2].replace("text = helpers + 'Lemma","text = helpers + round_text + 'Lemma")
open(p,'w').write('\n'.join(L))
