out='''From BB8 Require Import Lib016582 Individual82.
From Coq Require Import Lia PeanoNat.
Set Default Goal Selector "!".

Notation "c --> c'" := (c -[ tm ]-> c')   (at level 40).
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

'''
for nm in ['N1','Z6','Z2','N2','N3a','N2p','C1','N2s','N3p']:
    t=open('ph_%s.txt'%nm).read()
    i=t.index('Lemma %s :'%nm)
    j=t.index('Proof.',i)
    out+=t[i:j]+'Admitted.\n\n'
out+=open('main.v.in').read()
open('../../proofs/MainTest016582.v','w',newline='\n').write(out)
