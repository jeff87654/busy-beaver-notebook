s=open('glue35.v').read()
i=s.index("Lemma R4 :")
s=s[:i]+'''Lemma TLPS : forall T t J,
  ([0;1]^^T *> 1 >> 1 >> const 0) <{{C}} ([1;0;1]^^t *> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> 1 >> [0;0;1]^^J *> 0 >> 1 >> 0 >> const 0) -->*
  (1 >> 1 >> const 0) <{{C}} ([1;0;1]^^(2 * T + t) *> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> 1 >> [0;0;1]^^J *> 0 >> 1 >> 0 >> const 0).
Proof.
  induction T; intros.
  - finish.
  - eapply evstep_trans; [apply progress_evstep, (TLP J T t) |].
    follow (IHT (S (S t)) J).
    finish.
Qed.

Lemma R4 : forall M b, exists c, Kc (repeat O (S M)) O b -->* c /\ halted tm c.
Proof.
  intros. unfold Kc. rewrite lft_blank.
  destruct (FIN M (2 * S (S (S (S (6 * b)))) + 1)) as [c [H1 H2]].
  exists c. split; [| exact H2].
  follow (ROUNDS (S (3 * b)) O 2 ([1;0]^^(S (3 * O)) *> 1 >> [1;0;1]^^(S M) *> const 0)).
  replace (2 * S (3 * b) + 2) with (S (S (S (S (6 * b))))) by lia.
  eapply evstep_trans; [apply progress_evstep, (E3 M (S (S (S (S (6 * b))))) (const 0)) |].
  follow (HOPS M 1 (S (S (S (S (6 * b))))) (const 0)).
  follow (X4 M (S (S (S (S (6 * b)))))).
  follow (TLPS (S (S (S (S (6 * b))))) 6 M).
  replace (2 * S (S (S (S (6 * b)))) + 6) with (S (S (S (S (S (2 * S (S (S (S (6 * b)))) + 1)))))) by lia.
  exact H1.
Qed.
'''
open('glue35.v','w').write(s)
