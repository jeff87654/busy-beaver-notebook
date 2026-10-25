# shrink.py "COMPRESSED_TAPE" gap Q [count->new ...] : expand a kmom2 compressed K-moment tape, optionally replacing run counts
# (rules "i:new" by run index among (w)^k. tokens), print "cells head Q" for kmom.
import sys, re
ts, gap, Q = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rep = dict((int(a), int(b)) for a, b in (x.split(':') for x in sys.argv[4:]))
out = ''; idx = 0
for m in re.finditer(r'\(([01]+)\)\^(\d+)\.|([01])', ts):
    if m.group(1): k = rep.get(idx, int(m.group(2))); out += m.group(1) * k; idx += 1
    else: out += m.group(3)
print(out + '0' * (gap + 1), len(out) + gap, Q)
