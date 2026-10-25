import sys, re
src=sys.argv[1]
s=open(src).read()
i=s.index('Lemma St0 :')
a=s[:i]
j=s.index('(** ** Families, the cycle and its iteration *)')
k=s.index('Lemma StartL')
a+= s[j:k]
open('coq/PartA.v','w',newline='\n').write(a)
def grab(name):
    i=s.index('Lemma %s :'%name); j=s.index('Qed.',i)+4
    return s[i:j]
hdr='From BB8 Require Import Individual82.\nFrom Scratch Require Import PartA.\nFrom Coq Require Import Lia PeanoNat.\nSet Default Goal Selector "!".\n\n'
names=re.findall(r'^Lemma (St\d+|Hs\d+|End1|Init) :', s, re.M)
for nm in names:
    open('coq/T_%s.v'%nm,'w',newline='\n').write(hdr+grab(nm)+'\n')
print(' '.join(names))
