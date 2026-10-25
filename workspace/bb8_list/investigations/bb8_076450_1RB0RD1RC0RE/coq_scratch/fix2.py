t = open('body4.v.in').read()
t = t.replace("Proof. unfold Mc, T2. simpl. do 82 step. Show. Admitted.", "Proof. unfold Mc, T2. simpl. do 82 step. finish. Qed.")
t = t.replace("intros [[a [| b]] [|]]; simpl Inv.", "intros [[a [| b]] [|]]; cbn beta iota delta [Inv].")
for w in ["exists (4, 2 * a + 2, false)%nat.", "exists (4, 2 * a + 1, true)%nat.", "exists (6 * a + 6, b, true)%nat.", "exists (6 * a + 6, b, false)%nat."]:
    t = t.replace(w, w + " cbn beta iota delta [Inv].")
open('body4.v.in', 'w').write(t)
