"""Fill bound.v.in with the halting configuration of the generated EV_HALT lemma.  python gen_bound.py OUT.v"""
import re, sys
from pathlib import Path
src = (Path(__file__).resolve().parents[2] / 'proofs' / 'BB10_n1.v').read_text()
m = re.search(r'Lemma EV_HALT_halted : forall f k w, halted tm \(\((.*?)\) <\{\{J\}\} \((.*?)\)\)\.', src)
L, R = m.group(1), m.group(2)
assert L.endswith('[1;0;1;0;1]^^k *> const 0') and R.endswith('[1;0]^^f *> 0 >> 1 >> 0 >> 1 >> [1;0;1]^^w *> const 0')
lcells = [int(x) for x in L[:-len('[1;0;1;0;1]^^k *> const 0')].split('>>') if x.strip()]
rcells = [int(x) for x in R[:-len('[1;0]^^f *> 0 >> 1 >> 0 >> 1 >> [1;0;1]^^w *> const 0')].split('>>') if x.strip()]
head, ltail = lcells[0], lcells[1:]
assert head == 0
S = lambda cs: '[' + ';'.join('S%d' % c for c in cs) + ']'
const = sum(ltail) + sum(rcells) + 2
chalt = '(%s)%%sym <{{J}} (%s)%%sym' % (L, R)
text = Path('bound.v.in').read_text()
text = text.replace('@CHALT@', chalt).replace('@LLIST@', '%s ++ [S1;S0;S1;S0;S1]^^k' % S(ltail)) \
    .replace('@RLIST@', '%s ++ [S1;S0]^^f ++ [S0;S1;S0;S1] ++ [S1;S0;S1]^^w' % S(rcells)).replace('@C@', str(const))
Path(sys.argv[1]).write_text(text, newline='\n')
print('const', const, 'ltail', ltail, 'r', rcells)
