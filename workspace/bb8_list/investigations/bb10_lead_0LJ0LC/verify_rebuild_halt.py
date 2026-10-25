"""Sweep the rebuild C(0^m | b) -> N(6, 1^(4b+m+6), 1) and the halt N(0, 1^L, 2b+1) -> HALT (J reads 0), ones 2b+2L+5.
Also records the step counts, to fit exact formulas."""
import sys
from verify_rules import check, run
cases = []
for m in list(range(1, 31)) + [27]:
    for b in range(0, 61):
        cases.append([1] * m + [2 * b + 1])
for b in list(range(61, 400, 7)) + [997, 1000, 1001, 1002, 1003, 2047, 2048]:
    cases.append([1] * 27 + [2 * b + 1])
bad, stats = check(cases)
print('rebuild sweep', len(cases), stats, 'bad', bad)
cases = []
for L in range(1, 61):
    for b in list(range(0, 41)) + [100, 255, 256, 1000]:
        cases.append([0] + [1] * L + [2 * b + 1])
bad2, stats = check(cases)
print('halt sweep', len(cases), stats, 'bad', bad2)
sys.exit(1 if bad or bad2 else 0)
