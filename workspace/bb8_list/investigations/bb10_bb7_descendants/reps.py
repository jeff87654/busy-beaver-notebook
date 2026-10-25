"""Class representatives from behaviour signatures: python reps.py SIGS.tsv SETFILES... > reps.tsv
One machine per signature class (first in file order), tagged with the class size and its set tag."""
import sys
from collections import OrderedDict
sig = OrderedDict()
for l in open(sys.argv[1]):
    m, s = l.rstrip('\n').split('\t')
    sig.setdefault(s, []).append(m)
tags = {}
for fn in sys.argv[2:]:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        tags.setdefault(f[0], f[1] if len(f) > 1 else '')
for s, ms in sig.items():
    print(f'{ms[0]}\t{tags.get(ms[0], "")}:n{len(ms)}')
