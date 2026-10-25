"""summarize.py TAG... : verdict counts of runs/mf_TAG.tsv (+ renum summary) and the flagged rows.
Per b0 column 'b:kindA/kindB/stages/cycles/grow/last'.  Verdict per machine (worst over b0):
  FLAG-GH    : run A halts after >= 2 growing periods (grow-and-count shape)
  GROW+HALT1 : run A halts after exactly 1 growing period
  GROWER     : >= 2 growing periods, no halt seen (loop / max stages)
  HALT       : run A halts with no growing period
  UNFOLLOW   : TIME/WIDE before the first jump (no champion K-moment reached in 3e6 steps)
  OTHER      : the rest (TIME/WIDE/FAIL after jumps without growth, non-growing loops)"""
import sys, collections
RANK = ['FLAG-GH', 'GROW+HALT1', 'GROWER', 'HALT', 'OTHER', 'UNFOLLOW']
def verdict(col):
    b, _, rest = col.partition(':')
    ka, kb, st, cyc, gr, last = rest.split('/', 5)
    st, gr = int(st), int(gr)
    if ka == 'HALT' and gr >= 2: return 'FLAG-GH'
    if ka == 'HALT' and gr == 1: return 'GROW+HALT1'
    if gr >= 2: return 'GROWER'
    if ka == 'HALT': return 'HALT'
    if ka in ('TIME', 'WIDE') and st == 0: return 'UNFOLLOW'
    return 'OTHER'
import os
for tag in sys.argv[1:]:
    br = tag.startswith('br:'); tag = tag[3:] if br else tag
    rn = [l for l in open(f'runs/renum_{tag}.tsv') if l.startswith('#summary')] if not br else ['#branch']
    cnt = collections.Counter(); flags = []
    for l in open(f'runs/{"mfbr" if br else "mf"}_{tag}.tsv'):
        f = l.rstrip('\n').split('\t')
        import re
        vs = [verdict(c) for c in f[1:] if re.match(r'b\d+:', c)]
        v = min(vs, key=RANK.index)
        cnt[v] += 1
        if v in ('FLAG-GH', 'GROW+HALT1'):
            flags.append((v, f[0], f[1:]))
    print(tag, rn[0].strip() if rn else 'renum?', dict(cnt))
    for v, m, cols in flags:
        print('   ', v, m, ' '.join(cols))
