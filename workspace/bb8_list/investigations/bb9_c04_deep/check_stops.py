"""check_stops.py SURVEYFILES... : compare the survey's residue-stop sequence (C<n'> entries before ESC/HALT) with the chain formulas
   (L0 = 3k-5; stops at L = 0 mod 5, L >= 30 give n' = (L-25)/5).  Reports mismatches."""
import sys
sys.path.insert(0, '.')
from chain_model import step, THR
bad = 0; tot = 0
for f in sys.argv[1:]:
    for line in open(f):
        p = line.split()
        if not p or not p[0].isdigit(): continue
        k = int(p[0]); seq = p[1:p.index('|')] if '|' in p else p[1:]
        if seq and seq[0] in ('a', 'b', 'c', '?', 'cont'): seq = seq[1:]
        obs = [int(s[1:]) for s in seq if s.startswith('C')]
        # formula prediction: iterate from L0 until L < THR; collect n' at stops (L>=30 -> n'=(L-25)/5 then L0'=3n'-5)
        pred = []; L = 3 * k - 5
        while L >= THR:
            if L % 5 == 0: pred.append((L - 25) // 5)
            L = step(L)
        # also small-L stops that the TM makes: L in {40,55} (L>=30, <THR) -> n' = 3, 6
        if L % 5 == 0 and L >= 30: pred.append((L - 25) // 5)
        tot += 1
        if obs != pred: bad += 1; print('MISMATCH k=%d obs=%s pred=%s | %s' % (k, obs, pred, line.strip()[:100]))
print('checked', tot, 'mismatches', bad)
