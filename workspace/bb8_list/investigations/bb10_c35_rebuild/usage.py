"""Which (state,symbol) slots does the BB(8) record use in each phase?"""
import sys
sys.path.insert(0, '../bb8_champ35_1RB0RA_1LC0RH')
from tmlit import Sim, ST
from e0probe import TM, start, kword
sys.path.insert(0, '../bb8_champ35_1RB0RA_1LC0RH')
from fam import parse

def fmt(u):
    return ' '.join(f'{ST[q]}{s}:{c}' for (q, s), c in sorted(u.items()))

# start-up from blank
s = Sim(TM, 1 << 16); s.usage = {}
while s.steps < 6397:
    s.step()
print('startup', s.steps, parse(s), fmt(s.usage))
allc = set(s.usage)
# R1-R3 on sample configurations, one K-successor each
cases = [([0, 0, 2], 1, 0), ([0, 0, 2], 0, 3), ([1, 2], 0, 2), ([0, 3, 1], 0, 1), ([2], 0, 0), ([0, 0, 0, 1], 0, 4), ([5, 0, 1], 2, 7)]
uR = {}
for ds, a, b in cases:
    s = start(ds, a, b); s.usage = {}
    while True:
        s.step()
        if parse(s) is not None: break
    print('R', ds, a, b, '->', parse(s), s.steps)
    for k, v in s.usage.items(): uR[k] = uR.get(k, 0) + v
print('R1-R3', fmt(uR))
# R4 up to E0
s = start([0, 0, 0], 0, 2); s.usage = {}
while s.step(): pass
print('R4', s.steps, fmt(s.usage))
print('used only in R4:', sorted(f'{ST[q]}{x}' for (q, x) in set(s.usage) - set(uR) - allc))
print('not used in R1-R3:', sorted(f'{ST[q]}{x}' for q in range(8) for x in (0, 1) if (q, x) not in uR))
print('not used in startup:', sorted(f'{ST[q]}{x}' for q in range(8) for x in (0, 1) if (q, x) not in allc))
