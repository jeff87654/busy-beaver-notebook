s=open('abs35.v').read()
i=s.index("Lemma ltds_R3")
j=s.index("Lemma decomp")
new='''Lemma ltds_R3 : forall M y t x,
  ltds (repeat O M ++ x :: y :: t) (repeat O (S M) ++ S y :: t).
Proof.
  intros. unfold ltds.
  assert (E1 : rev (repeat O M ++ x :: y :: t) = rev t ++ y :: x :: repeat O M).
  { rewrite rev_app_distr. simpl. rewrite rev_rep. rewrite <- !app_assoc. reflexivity. }
  assert (E2 : rev (repeat O (S M) ++ S y :: t) = rev t ++ S y :: repeat O (S M)).
  { rewrite rev_app_distr. simpl. rewrite rev_rep. rewrite <- app_assoc. reflexivity. }
  rewrite E1, E2.
  apply lex_pre. apply lex_hd; [lia |]. simpl. rewrite len_rep. reflexivity.
Qed.

'''
open('abs35.v','w').write(s[:i]+new+s[j:])
