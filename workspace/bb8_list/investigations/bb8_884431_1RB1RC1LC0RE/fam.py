import sys
sys.path.insert(0, '../neighbors_family_tools')
from tmlit import Sim, ST
TM = '1RB1RC_1LC0RE_1LF1LD_1LA1LE_1RH1RF_0LF1LG_0LD1LA_---0RA'

def parse(K):
    """K = '111' + tokens (10 unit | 11 sep). Return list of unit-run lengths (n+2 of them: ds..., a, 2b+1) or None."""
    if not K.startswith('111') or len(K) % 2 == 0: return None
    toks = [K[i:i+2] for i in range(3, len(K), 2)]
    runs, cur = [], 0
    for t in toks:
        if t == '10': cur += 1
        elif t == '11': runs.append(cur); cur = 0
        else: return None
    if not toks or cur != 0 or toks[-1] != "11": return None
    return runs     # ds (farthest first), a, 2b+1

def fam_at(s):
    if ST[s.state] != 'A' or any(s.tape[s.lo:s.pos]) or s.tape[s.pos] != 0: return None
    w = ''.join(map(str, s.tape[s.pos+1:s.hi+1])).rstrip('0')
    return parse(w[::-1])

if __name__ == '__main__':
    s = Sim(TM)
    N = int(sys.argv[1]); lim = int(sys.argv[2])
    n = 0
    while s.steps < N and n < lim:
        r = fam_at(s)
        if r is not None:
            print(s.steps, r); n += 1
        if not s.step(): print('halt'); break
