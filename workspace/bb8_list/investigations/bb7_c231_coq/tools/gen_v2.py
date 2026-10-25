"""Adapt the proved coq/ files to the BB7/verify layout in v2/ (logical root BB7, definitions in Defs.v)."""
import os, re
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(W, 'coq'); DST = os.path.join(W, 'v2')
ren = {'BB72': 'BB72', 'Individual72': 'Individual72', 'Clr': 'Clr', 'Bound': 'Bound', 'Bound3': 'Bound3',
       'T1': 'C231_rules1', 'T2': 'C231_rules2', 'T3': 'C231_rules3', 'T4': 'C231_init', 'T5': 'C231_clear',
       'T6': 'C231_run', 'M231': 'C231_main',
       'U1': 'C232_rules1', 'U2': 'C232_rules2', 'U3': 'C232_rules3', 'U4': 'C232_init', 'U5': 'C232_clear',
       'U6': 'C232_run', 'M232': 'C232_main'}
def rd(n): return open(os.path.join(SRC, n + '.v'), encoding='utf-8').read()
def cut(s, a, b):
    i = s.index(a); j = s.index(b, i) + len(b); return s[:i] + s[j:]
def fiximp(s):
    s = re.sub(r'From BB8 Require (Import|Export) ([^.]*)\.',
               lambda m: 'From BB7 Require ' + m.group(1) + ' ' + ' '.join(ren.get(x, x) for x in m.group(2).split()) + '.', s)
    assert 'BB8' not in s.replace('bb8', '').replace('BB8_', ''), 'BB8 left'
    return s
out = {}
out['BB72'] = rd('BB72')
out['Individual72'] = fiximp(rd('Individual72'))
s = rd('Clr')
s = cut(s, 'Fixpoint iter', 'end.\n\n')
s = cut(s, 'Fixpoint UW', 'Definition W (j : nat) : nat -> nat := snd (UW j).\n\n')
s = s.replace('From Coq Require Import Lia PeanoNat List.', 'From BB7 Require Import Defs.\nFrom Coq Require Import Lia PeanoNat List.')
s = s.replace('(** U j x : the counter', '(** (iter, UW, U, W are defined in Defs.v.)  U j x : the counter')
out['Clr'] = s
s = rd('Bound')
s = cut(s, 'Fixpoint arrow (k a b : nat) : nat :=', 'end.\n\n')
s = s.replace('(** arrow k a b = a ^(k arrows) b (Knuth), with 0 arrows = multiplication. *)\n', '(** arrow (Knuth\'s up-arrows) is defined in Defs.v. *)\n')
out['Bound'] = fiximp(s.replace('From BB8 Require Import Clr.', 'From BB8 Require Import Defs Clr.'))
out['Bound3'] = fiximp(rd('Bound3').replace('From BB8 Require Import Clr Bound.', 'From BB8 Require Import Defs Clr Bound.'))
for pre, n in (('T', 231), ('U', 232)):
    s = rd(pre + '1')
    i = s.index('Definition tm : TM'); j = s.index('  end.\n', i) + len('  end.\n')
    s = s[:i] + f'(* the table tm{n} is in Defs.v *)\nNotation tm := tm{n} (only parsing).\n' + s[j:]
    s = s.replace('From BB8 Require Import Individual72.', 'From BB8 Require Import Individual72.\nFrom BB8 Require Export Defs.')
    out[pre + '1'] = fiximp(s)
    for k in '2345':
        out[pre + k] = fiximp(rd(pre + k))
    s = rd(pre + '6')
    s = cut(s, '(** ** Counting ones *)', 'N = count1 L + sym_val s + count1 R.\n\n')
    out[pre + '6'] = fiximp(s.replace('(** ** Main results', '(** (sym_val, count1, ones are defined in Defs.v.) *)\n\n(** ** Main results'))
    out['M%d' % n] = fiximp(rd('M%d' % n))
for k, v in out.items():
    open(os.path.join(DST, ren[k] + '.v'), 'w', encoding='utf-8', newline='\n').write(v.replace('\r\n', '\n'))
print('wrote', len(out))
