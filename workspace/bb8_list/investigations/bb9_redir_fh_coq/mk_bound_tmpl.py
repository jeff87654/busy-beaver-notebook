"""Build bound_fh.v.in from the 0LA bound template plus sibling-specific parts."""
from pathlib import Path
src = Path('../bb9_redir_0LA_coq/bound.v.in').read_text()


def cut(a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


counting = cut('(** ** Counting ones', '(** ** The exact score *)')
old = '''Lemma ones_c_halt : forall i r n, ones (c_halt i r (lfr (repeat 9 n))) (6 * i + 2 * r + 10 * n + 29).'''
assert old in counting
counting = counting.replace(old, '''Lemma ones_c_halt : forall a u n, ones (c_halt a u (lfr (repeat 9 n))) (86 + 9 * u + a + 10 * n).''')
growth = cut('(** ** Growth facts for base-2 arrows *)', 'Theorem sigma_lower_bound')
growth = growth.replace(cut('Lemma arrow_level :', 'Lemma arrow_double'), '').replace(cut('Lemma arrow_double', 'Lemma arrow_succ'), '')
cmp = cut('(** ** Comparison with the BB(9) record', 'Print Assumptions score_exact.')
i = cmp.index('(** The BB(9) record 1RB0RA')
j = cmp.index('(** The comparison with the record', i)
cmp = cmp[:i] + cmp[j:]
old = '''  destruct (beats_record_formula BB9_record_1RB0RA.Bx HBx) as [co [No [Ho1 [Ho2 [Ho3 Hlt]]]]].'''
assert old in cmp
cmp = cmp.replace(old, '''  destruct beats_0LA_formula as [co [No [Ho1 [Ho2 [Ho3 Hlt0]]]]].
  pose proof (compare_arith BB9_record_1RB0RA.Bx bf nn KK (bf_vs_Bx BB9_record_1RB0RA.Bx HBx)
                (Bx_ge6 BB9_record_1RB0RA.Bx HBx) nn_ge KK_eq) as Hlt1.''')
old = '''  split; [exact Ho1 | split; [exact Ho2 | split; [exact Ho3 | exact Hlt]]].'''
assert old in cmp
cmp = cmp.replace(old, '''  split; [exact Ho1 | split; [exact Ho2 | split; [exact Ho3 |]]].
  revert Hlt0 Hlt1.
  set (A := 3 * arrow (12 * BB9_record_1RB0RA.Bx - 9) 2 8 + 108 * (BB9_record_1RB0RA.Bx / 5) + 70) in *.
  set (B := 3 * arrow (KK + 2) 2 5 + 10 * nn + 6 * (KK / 5) + 11) in *. clearbody A B. intros. lia.''')
head = Path('bound_fh_head.v.in').read_text()
score = Path('bound_fh_score.v.in').read_text()
tail = '''
Print Assumptions score_exact.
Print Assumptions score_closed.
Print Assumptions sigma_lower_bound.
Print Assumptions beats_0LA_formula.
Print Assumptions beats_record.
'''
Path('bound_fh.v.in').write_text(head + counting + growth + score + cmp + tail, newline='\n')
print('ok')
