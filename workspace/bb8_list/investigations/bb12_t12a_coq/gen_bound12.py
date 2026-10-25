"""Fill bound12.v.in (score of T12a) with the halting configurations of EV_HALT1/2 and the EAT lemmas with ones.
  python gen_bound12.py SRC_BB12_T12a.v OUT.v"""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
src = Path(sys.argv[1]).read_text()

def halted(name):
    m = re.search(r'Lemma EV_%s_halted : forall [^,]*, halted tm \(\((.*?)\) \{\{L\}\}> \((.*?)\)\)\.' % name, src)
    L, R = m.group(1), m.group(2)
    assert R.startswith('1 >> ')
    return L, R[len('1 >> '):]

H1L, H1R = halted('HALT1')
H2L, H2R = halted('HALT2')
G3 = re.search(r'Definition G3OUT \(b : nat\) \(l : side\) : side := \((.*?)\)%sym\.', src).group(1)
PRE2 = '0 >> 0 >> 0 >> 0 >> 1 >> [0;0;0;0;0;1]^^b *> 0 >> 0 >> 1 >> 1 >> 1 >> 0 >> 1 >> 1 >> '
assert G3.startswith(PRE2)
REST2 = G3[len(PRE2):]
assert H2L.endswith('>> l')
H2L = H2L[:-1] + '(' + REST2 + ')'
OUT = {0: '(repeat 1 3 ++ [0] ++ repeat 1 3 ++ [4 + A; 0; 4; 2])',
       2: '(repeat 1 3 ++ [0; 7 + A; 0; 2; 0] ++ repeat 1 5 ++ [10])',
       4: '(repeat 1 3 ++ [0; 7 + A; 2] ++ repeat 1 1 ++ [0; 0; 0] ++ repeat 1 2 ++ [2] ++ repeat 1 6 ++ [0; 9; 4])'}
EAT = r'''
Lemma EAT@R@_ones : forall A K j x l, side_ones l 0 -> exists Sd,
  Bf (S20 (6 + K) l) (repeat 1 4 ++ blocks (6 + 6 * j + @R@) ++ [0; 2; 9 + x; 0; 2; 2]) (4 + A) -->* Bf Sd @OUT@ 6 /\
  side_ones Sd j.
Proof.
  intros A K j x l Hl. eexists. split.
  - rewrite (blocks_add (6 + 6 * j) @R@), (blocks_add 6 (6 * j)).
    replace (repeat 1 4 ++ blocks 6 ++ blocks (6 * j) ++ blocks @R@ ++ [0; 2; 9 + x; 0; 2; 2])
      with ((repeat 1 4 ++ blocks 6) ++ blocks (6 * j) ++ blocks @R@ ++ [0; 2; 9 + x; 0; 2; 2])
      by (rewrite <- app_assoc; reflexivity).
    rewrite Bf_app, lfr_blocks6. unfold FLAT, S20.
    apply W_EAT@R@.
  - repeat apply so_cons. eapply so_le; [apply so_pow; so_tac | cbn [count1 sym_val]; lia].
Qed.
'''
eats = ''.join(EAT.replace('@R@', str(r)).replace('@OUT@', OUT[r - r % 2]) for r in range(6))
text = (HERE / 'bound12.v.in').read_text()
text = text.replace('@H1L@', H1L).replace('@H1R@', H1R).replace('@H2L@', H2L).replace('@H2R@', H2R) \
    .replace('@REST2@', REST2).replace('@EATS@', eats)
Path(sys.argv[2]).write_text(text, newline='\n')
print('wrote', sys.argv[2], len(text))
