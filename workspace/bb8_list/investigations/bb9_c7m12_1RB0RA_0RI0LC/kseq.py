"""Compress kcanon output: show a K configuration only when its token list (without the trailing raw b-part and
the in-progress R1 counter token) changes.  usage: ./kprobe.sh ... | python kseq.py"""
import re
import sys

prev = None
for line in sys.stdin:
    line = line.rstrip()
    if not line.startswith('K '):
        if line.startswith('AE') or line.startswith('HALT'):
            print('  ' + line[:200])
        continue
    step, toks = line[2:].split(' | ', 1)
    t = re.sub(r'\s*<[^>]*>\s*$', '', toks).split()
    key = ' '.join(t)
    if key != prev:
        print(f'{step:>9} | {toks[:170]}')
        prev = key
