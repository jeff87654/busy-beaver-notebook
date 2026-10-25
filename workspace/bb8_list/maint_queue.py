"""Maintenance helper for the check-in: dedup the investigator queue and list new machines for the digit-list scan.

  python maint_queue.py            # dry run: print the counts
  python maint_queue.py --apply    # also record duplicates in investigations/dispatched.txt and write
                                   # neighbors/ack_new.txt (doubling rows not yet in neighbors/ack_scanned.txt)

Queue = the doubling rows of followup/promising.tsv that are neither dispatched nor decided by the pre-filter.
Queue rows that dedup.py matches to a known machine are recorded as "duplicate of X".
"""
import json
import sys
import time
from pathlib import Path

import dedup

ROOT = Path(__file__).resolve().parent
DISP = ROOT / 'investigations' / 'dispatched.txt'
SCANNED = ROOT / 'neighbors' / 'ack_scanned.txt'
NEW = ROOT / 'neighbors' / 'ack_new.txt'


def main():
    apply = '--apply' in sys.argv
    rows = (ROOT / 'followup' / 'promising.tsv').read_text().splitlines()[1:]
    doubling = [l.split('\t')[-1].strip() for l in rows if l.startswith('doubling\t')]
    dispatched = {l.split('\t')[0] for l in DISP.read_text().splitlines() if l.strip()} if DISP.exists() else set()
    pf = json.loads((ROOT / 'prefilter_results.json').read_text())
    decided = {m for m, r in pf.items() if r['status'] == 'verified_nonhalting'}
    queue = [m for m in doubling if m not in dispatched and m not in decided]
    dups = {m: h for m, h in dedup.check(queue).items() if h}
    scanned = set(SCANNED.read_text().split()) if SCANNED.exists() else set()
    new = [m for m in doubling if m not in scanned]
    if apply:
        stamp = time.strftime('%Y-%m-%d_%H:%M')
        with open(DISP, 'a', newline='\n') as f:
            for m, h in dups.items():
                f.write(f'{m}\t{stamp}\tduplicate of {h}\n')
        NEW.write_text(''.join(m + '\n' for m in new), newline='\n')
    for m, h in dups.items():
        print('duplicate', m, 'of', h)
    print(f'doubling rows {len(doubling)}; queue {len(queue) - len(dups)} (after {len(dups)} new duplicates); '
          f'digit-list scan: {len(new)} new, {len(scanned)} scanned before')


if __name__ == '__main__':
    main()
