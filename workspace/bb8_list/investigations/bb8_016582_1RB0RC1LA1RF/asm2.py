import sys, glob, os
from gen_base import table
TM = "1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF"
NL = chr(10)
subst = dict(tm=TM, table=table(TM))
P = '../../proofs/'
def wr(fn, txt):
    if os.path.exists(fn) and open(fn).read() == txt:
        return
    open(fn, 'w', newline=NL).write(txt)
head = open('head.v.in').read() % subst
lib = head + open('libextra.v.in').read() + open('lib_cross.txt').read()
wr(P + 'Lib016582.v', lib)
pre = open('phhead.v.in').read()
for f in glob.glob('ph_*.txt'):
    nm = f[3:-4]
    z2x = open('zfuse2.v.in').read() if nm in ('N2p', 'C1', 'N2s') else ''
    extra = {'N2p': 'From BB8 Require Import Ph016582_Z2.' + NL, 'C1': 'From BB8 Require Import Ph016582_Z6.' + NL, 'N2s': 'From BB8 Require Import Ph016582_Z6.' + NL}.get(nm, '')
    wr(P + 'Ph016582_%s.v' % nm, extra + pre + (open('rep6.v.in').read() if nm in ('N2p', 'C1', 'N2s') else '') + open(f).read())
