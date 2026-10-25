"""Translate the RPN clause programs of zf2.py into symbolic wff terms (Coq syntax) for Enum.v.

Each clause is a list of stack words over: v_0..v_3 (push var), par1..par3 (push param), weq wel wim wn wal wex wa.
Stack discipline: tw = top, ws = rest; a push word pushes tw onto ws and sets tw; a binary word combines
(second, top) -> cons'd code.  We only need the resulting top wff symbolically.
"""
import re, sys

AXIOMS = {
 'DET': 'par3 par1 wim',
 'GEN': 'par1 par3 wal',
 'B1':  'par1 par2 wim par2 par3 wim par1 par3 wim wim wim',
 'B2':  'par1 wn par1 wim par1 wim',
 'B3':  'par1 par1 wn par2 wim wim',
 'B4':  'par1 par2 par3 wim wal par1 par2 wal par1 par3 wal wim wim',
 'B6b': 'par1 par2 par3 wal wal par2 par1 par3 wal wal wim',
 'B8b': 'par1 par2 weq par1 par3 wel par2 par3 wel wim wim',
 'B6a': 'par1 par2 weq par3 par1 par2 weq wal wim par1 par2 wel par3 par1 par2 wel wal wim wa',
 'B6c': 'par1 par1 par2 wal wex par2 wim',
 'B7':  'par1 par1 par2 weq wex',
 'B8a': 'par1 par2 weq par1 par3 weq par2 par3 weq wim wim',
 'B8c': 'par1 par2 weq par3 par1 wel par3 par2 wel wim wim',
 'EXT': 'v_2 v_2 v_0 wel v_2 v_1 wel wim v_2 v_1 wel v_2 v_0 wel wim wa wal v_0 v_1 weq wim',
 'REP': 'v_3 v_1 v_2 v_1 par1 wal v_2 v_1 weq wim wal wex wal v_1 v_2 v_2 v_1 wel v_3 v_3 v_0 wel v_1 par1 wal wa wex wim v_3 v_3 v_0 wel v_1 par1 wal wa wex v_2 v_1 wel wim wa wal wex wim',
 'POW': 'v_1 v_2 v_3 v_3 v_2 wel v_3 v_0 wel wim wal v_2 v_1 wel wim wal wex',
 'UNI': 'v_1 v_2 v_3 v_2 v_3 wel v_3 v_0 wel wa wex v_2 v_1 wel wim wal wex',
 'INF': 'v_1 v_0 v_1 wel v_0 v_0 v_1 wel v_2 v_2 v_1 wel v_1 v_1 v_2 wel v_1 v_0 weq wim v_1 v_0 weq v_1 v_2 wel wim wa wal wa wex wim wal wa wex',
}
# zf2.py axioms() list order (index -> clause), then AXIOMORDER positions
INDEX = ['DET','GEN','B1','B2','B3','B4','B6b','B8b','B6a','B6b','B6c','B7','B8a','B8b','B8c','EXT','REP','POW','UNI','INF']
AXIOMORDER = [16, 17, 3, 18, 4, 7, 8, 9, 11, 5, 12, 13, 14, 2, 15, 0, 1, 6, 10, 19]

def rpn(words):
    st = []
    for w in words.split():
        if w.startswith('v_'): st.append(f'c{w[2]}')          # variable code i
        elif w.startswith('par'): st.append(f'p{w[3]}')
        elif w in ('weq','wel','wim','wal','wa'):
            y = st.pop(); x = st.pop(); st.append(f'({w} {x} {y})')
        elif w in ('wn','wex'):
            x = st.pop(); st.append(f'({w} {x})') if w == 'wn' else st.append(f'(wex {x})')
        else: raise ValueError(w)
    assert len(st) == 1, (words, st)
    return st[0]

# wex is a unary op on (x, ph): stack x ph -> E. x ph : wn wal wn => wn (wal x (wn ph)); as binary on stack
def rpn2(words):
    st = []
    for w in words.split():
        if w.startswith('v_'): st.append(f'c{w[2]}')
        elif w.startswith('par'): st.append(f'p{w[3]}')
        elif w in ('weq','wel','wim','wal','wa','wex'):
            y = st.pop(); x = st.pop(); st.append(f'({w} {x} {y})')
        elif w == 'wn':
            x = st.pop(); st.append(f'(wn {x})')
        else: raise ValueError(w)
    assert len(st) == 1, (words, st)
    return st[0]

if __name__ == '__main__':
    print('(* clause wffs in zf2.py index order; c0..c4 = variable codes 0..4, p1..p3 = params *)')
    for i, name in enumerate(INDEX):
        print(f'(* {i:2d} {name:4s} *) Definition clause_{i} (p1 p2 p3 : nat) : nat := {rpn2(AXIOMS[name])}.')
    print('Definition axiomorder : list nat := [' + '; '.join(map(str, AXIOMORDER)) + '].')
    print('(* positions:', [INDEX[i] for i in AXIOMORDER], '*)')
