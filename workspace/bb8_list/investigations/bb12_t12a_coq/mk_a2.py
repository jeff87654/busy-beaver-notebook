"""abstract2_12.v.in = n1's abstract2.v.in + main.v.in with the period events and the period for any far side L."""
SENT = '(*@@SPLIT@@*)' + chr(10)
s = open('abstract2.v.in').read() + SENT + open('main.v.in').read()
def R(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b)
R("Definition FarP (k m : nat) : side := (0 >> 0 >> lfr (0 :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 (2 + k))%nat (const 0))%sym.",
  "Definition FarP (L : side) (k m : nat) : side := (0 >> 0 >> lfr (0 :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 (2 + k))%nat L)%sym.")
R("""Lemma P1_B : forall k m n a,
  Bf0 (repeat 1 n ++ 2 :: 0 :: 0 :: repeat 1 (6 + m) ++ 5 :: repeat 2 k) a -->*
  Bf0 (repeat 1 n ++ (3 + a) :: 1 :: 0 :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 (2 + k)) 6.
Proof. intros. bnorm. follow (EV_P1 a k m n). finish_norm. Qed.""",
"""Lemma P1_B : forall L k m n a,
  Bf L (repeat 1 n ++ 2 :: 0 :: 0 :: repeat 1 (6 + m) ++ 5 :: repeat 2 k) a -->*
  Bf L (repeat 1 n ++ (3 + a) :: 1 :: 0 :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 (2 + k)) 6.
Proof. intros. bnorm. follow (EV_LP1 a k m n L). finish_norm. Qed.""")
R("""Lemma P2_B : forall k m p r w,
  Bf0 (repeat 1 (1 + w) ++ 0 :: (1 + 3 * p) :: 1 :: 0 :: 0 :: 0 :: repeat 1 (6 + m) ++ 5 :: repeat 2 k) (1 + r) -->*
  Bf (FarP k m) (repeat 1 2 ++ repeat 1 w ++ repeat 1 (2 * p) ++ [2 + r; 2]) 4.""",
"""Lemma P2_B : forall L k m p r w,
  Bf L (repeat 1 (1 + w) ++ 0 :: (1 + 3 * p) :: 1 :: 0 :: 0 :: 0 :: repeat 1 (6 + m) ++ 5 :: repeat 2 k) (1 + r) -->*
  Bf (FarP L k m) (repeat 1 2 ++ repeat 1 w ++ repeat 1 (2 * p) ++ [2 + r; 2]) 4.""")
R("follow (EV_P2 k m p r w).", "follow (EV_LP2 k m p r w L).")
R("""Lemma P3_B : forall k m w a, Bf (FarP k m) (repeat 1 w ++ [2; 2]) a -->*
  Bf0 (repeat 1 w ++ (5 + a) :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 (2 + k)) 6.
Proof. intros. unfold FarP. bnorm. follow (EV_P3 a (2 + k) m w). finish_norm. Qed.""",
"""Lemma P3_B : forall L k m w a, Bf (FarP L k m) (repeat 1 w ++ [2; 2]) a -->*
  Bf L (repeat 1 w ++ (5 + a) :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 (2 + k)) 6.
Proof. intros. unfold FarP. bnorm. follow (EV_LP3 a (2 + k) m w L). finish_norm. Qed.""")
R("""Lemma P4_B : forall k m q r w,
  Bf0 (repeat 1 (1 + w) ++ 0 :: (3 * q) :: 0 :: 0 :: repeat 1 (2 + m) ++ 5 :: repeat 2 k) (1 + r) -->*
  Bf0 (repeat 1 2 ++ repeat 1 w ++ repeat 1 (2 * q) ++ (2 + r) :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 k) 4.""",
"""Lemma P4_B : forall L k m q r w,
  Bf L (repeat 1 (1 + w) ++ 0 :: (3 * q) :: 0 :: 0 :: repeat 1 (2 + m) ++ 5 :: repeat 2 k) (1 + r) -->*
  Bf L (repeat 1 2 ++ repeat 1 w ++ repeat 1 (2 * q) ++ (2 + r) :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 k) 4.""")
R("follow (EV_P4 k m q r w).", "follow (EV_LP4 k m q r w L).")
i = s.index('(** the halt: FarE k'); j = s.index(SENT)
s = s[:i] + s[j:]
R("Definition Per (k m n a : nat) : Q * tape := Bf0 (repeat 1 n ++ 2 :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 k) a.",
  "Definition Per (L : side) (k m n a : nat) : Q * tape := Bf L (repeat 1 n ++ 2 :: 0 :: 0 :: repeat 1 m ++ 5 :: repeat 2 k) a.")
R("Lemma PERIOD : forall k m n a, Inv n a ->\n  exists n' a', Per k (14 + m) n a -->* Per (4 + k) m n' a'",
  "Lemma PERIOD : forall L k m n a, Inv n a ->\n  exists n' a', Per L k (14 + m) n a -->* Per L (4 + k) m n' a'")
R("  intros k m n a [Hn [Ha Hb]].\n  destruct (r1_split a Ha) as [p Hp].\n  destruct n as [| n1]; [lia |]. destruct n1 as [| w]; [lia |].\n  destruct (r1_ge (S w) 3 ltac:(lia)) as [x [Hx [Hx1 _]]].\n  destruct (r1_ge (2 + w + 2 * p) x Hx1)",
  "  intros L k m n a [Hn [Ha Hb]].\n  destruct (r1_split a Ha) as [p Hp].\n  destruct n as [| n1]; [lia |]. destruct n1 as [| w]; [lia |].\n  destruct (r1_ge (S w) 3 ltac:(lia)) as [x [Hx [Hx1 _]]].\n  destruct (r1_ge (2 + w + 2 * p) x Hx1)")
R("follow (P1_B k (8 + m) (S (S w)) a).", "follow (P1_B L k (8 + m) (S (S w)) a).")
R("follow (DEP9 (const 0%sym) (S w) a (1 :: 0 :: 0 :: 0 :: repeat 1 (8 + m)", "follow (DEP9 L (S w) a (1 :: 0 :: 0 :: 0 :: repeat 1 (8 + m)")
R("follow (P2_B (2 + k) (2 + m) p (3 * x) w).", "follow (P2_B L (2 + k) (2 + m) p (3 * x) w).")
R("(FarP (2 + k) (2 + m)) 4 (or_intror r1_4)).", "(FarP L (2 + k) (2 + m)) 4 (or_intror r1_4)).")
R("follow (P3_B (2 + k) (2 + m) (2 + w + 2 * p)", "follow (P3_B L (2 + k) (2 + m) (2 + w + 2 * p)")
R("follow (DEP9 (const 0%sym) (1 + w + 2 * p)", "follow (DEP9 L (1 + w + 2 * p)")
R("follow (P4_B (4 + k) m (S y) (3 * x') (w + 2 * p)).", "follow (P4_B L (4 + k) m (S y) (3 * x') (w + 2 * p)).")
R("apply (CLR (2 + (w + 2 * p) + 2 * S y) x' 2 _ (const 0%sym) 4 (or_intror r1_4)).",
  "apply (CLR (2 + (w + 2 * p) + 2 * S y) x' 2 _ L 4 (or_intror r1_4)).")
R("Lemma PERIODS : forall J k n a, Inv n a ->\n  exists n' a', Per k (14 * J + 7) n a -->* Per (4 * J + k) 7 n' a'",
  "Lemma PERIODS : forall L r J k n a, Inv n a ->\n  exists n' a', Per L k (14 * J + r) n a -->* Per L (4 * J + k) r n' a'")
R("induction J as [| J IH]; intros k n a Hinv.", "intros L r. induction J as [| J IH]; intros k n a Hinv.")
R("destruct (PERIOD k (14 * J + 7) n a Hinv)", "destruct (PERIOD L k (14 * J + r) n a Hinv)")
R("replace (14 * S J + 7) with (14 + (14 * J + 7)) by lia.", "replace (14 * S J + r) with (14 + (14 * J + r)) by lia.")
R("exists w f, Per (4 + k) 7 n a -->*", "exists w f, Per (const 0%sym) (4 + k) 7 n a -->*")
R("follow (P1_B (4 + k) 1 (S (S w)) a).", "follow (P1_B (const 0%sym) (4 + k) 1 (S (S w)) a).")
# ENDGAME and reach_end also report the accumulator's residue and size and the far run length (T12a restarts there)
R("Per (const 0%sym) (4 + k) 7 n a -->* Bf (FarE k) (repeat 1 w ++ [0]) f /\\ F n <= w.",
  "Per (const 0%sym) (4 + k) 7 n a -->* Bf (FarE k) (repeat 1 w ++ [0]) f /\\ F n <= w /\\ r1 f /\\ 4 <= f.")
R("  - rewrite Hp in Hb. pose proof (growth (S (S w)) p ltac:(lia)). lia.\nQed.\n\n(** *** The run from the blank tape *)",
  "  - split; [rewrite Hp in Hb; pose proof (growth (S (S w)) p ltac:(lia)); lia |].\n"
  "    destruct (r1_ge (2 + w + 2 * p) (S x) ltac:(lia)) as [z [Hz [Hz1 _]]].\n"
  "    split; [exists z; lia | lia].\nQed.\n\n(** *** The run from the blank tape *)")
R("Lemma reach_end : exists k w f, c0 -->* Bf (FarE k) (repeat 1 w ++ [0]) f /\\ iter (2 * JJ + 1) F 34 <= w.",
  "Lemma reach_end : exists k w f, c0 -->* Bf (FarE k) (repeat 1 w ++ [0]) f /\\ iter (2 * JJ + 1) F 34 <= w /\\\n"
  "  r1 f /\\ 4 <= f /\\ 13 <= k.")
R("  destruct (ENDGAME (4 * JJ - 3) n a' Hinv') as [w [f [H2 Hw]]].\n  exists (4 * JJ - 3), w, f. split.",
  "  destruct (ENDGAME (4 * JJ - 3) n a' Hinv') as [w [f [H2 [Hw [Hf1 Hf4]]]]].\n  pose proof JJ_ge4 as HJ4.\n"
  "  exists (4 * JJ - 3), w, f. split; [| split; [| split; [exact Hf1 | split; [exact Hf4 | lia]]]].")
R("(** The last B-form before the halt;", "Lemma JJ_ge4 : 4 <= JJ.\nProof.\n  destruct T_mod7 as [s Hs]. pose proof T_ge as HT.\n"
  "  assert (E : (3 * T - 13) / 7 = 3 * s - 1).\n  { rewrite Hs. symmetry. apply Nat.div_unique with (r := 0); lia. }\n"
  "  unfold JJ. rewrite E. revert Hs HT. generalize T. intros. lia.\nQed.\n\n(** The last B-form before the halt;")
R("Lemma reach_per : exists a, c0 -->* Per 1 (6 * T - 19) 34 a /\ Inv 34 a.",
  "Lemma reach_per : exists a, c0 -->* Per (const 0%sym) 1 (6 * T - 19) 34 a /\ Inv 34 a.")
R("follow (P4_B 1 (6 * T - 19) 0 (3 * x0) 32).", "follow (P4_B (const 0%sym) 1 (6 * T - 19) 0 (3 * x0) 32).")
R("destruct (PERIODS JJ 1 34 a Hinv)", "destruct (PERIODS (const 0%sym) 7 JJ 1 34 a Hinv)")
# the old halt theorem is replaced by the restart chain (main12.v.in)
i = s.index('Theorem halt : halts tm c0.')
s = s[:i]
a, b = s.split(SENT)
open('abstract2_12.v.in', 'w', newline=chr(10)).write(a)
open('round1_12.v.in', 'w', newline=chr(10)).write(b)
print('ok', len(s))
