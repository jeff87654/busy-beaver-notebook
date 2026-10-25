import re
w = open('wrappers_end.v.in').read()
parts = re.split(r'(?=\nLemma W_)', '\n' + w)
keep = [p for p in parts if not p.startswith('\nLemma W_EAT')]
e = open('end.v.in').read()
i = e.index('\nLemma EAT0')
j = e.index('(** *** The continuations and the halt *)')
k = e.index('(** the block eating and its continuation')
etest = e[:i] + '\n' + e[j:k]
hdr = 'From BB8 Require Import Individual122.\nFrom Dev Require Import M M2a A R.\nFrom Coq Require Import Lia PeanoNat List.\nImport ListNotations.\nSet Default Goal Selector "!".\nSet Default Timeout 3000.\nLocal Open Scope nat_scope.\nOpaque U arrow.\n'
open('dev/E1.v', 'w', newline='\n').write(hdr + open('wrap_pre.v.in').read() + ''.join(keep) + etest)
