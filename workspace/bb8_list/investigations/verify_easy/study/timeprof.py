"""Aggregate coqc -time output by tactic kind.  python -I timeprof.py FILE.time.txt"""
import re, sys, collections
agg = collections.Counter(); cnt = collections.Counter(); tot = 0.0
for line in open(sys.argv[1], encoding='utf-8', errors='replace'):
    m = re.match(r'Chars \d+ - \d+ \[(.*)\] ([\d.]+) secs', line)
    if not m: continue
    cmd, t = m.group(1).replace('~', ' '), float(m.group(2)); tot += t
    k = cmd.split()[0] if cmd.split() else '?'
    if k in ('-', '+', '*'): k = cmd.split()[1] if len(cmd.split()) > 1 else k
    k = re.sub(r'\(.*', '', k)
    if k == 'do': k = 'do N step'
    agg[k] += t; cnt[k] += 1
print('total %.1f s' % tot)
for k, t in agg.most_common(15):
    print('  %-22s %8.1f s  %5.1f%%  (%d)' % (k, t, 100 * t / tot, cnt[k]))
