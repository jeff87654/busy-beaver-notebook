"""Look for Ce3-shaped visits in the blank-tape orbit (run-length simulator)."""
import sys
sys.path.insert(0, '/workspace/workspace/bb_champs_17_18')
from rsim import Sim

M = ('1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_1RN1RJ_'
     '1RE0LA_1RA0RF_1LH1LA_1RB1RM_1LO0LO_0LK1LO')


def ce3(Sim_s):
    """Check the run-length tape for the Ce3 shape with the head in state A."""
    if Sim_s.st != 'A' or Sim_s.face != 'R':
        return None
    R = Sim_s.R  # top first
    L = Sim_s.L
    # right must start with 1,0,1,0,... at least 2 pairs
    if len(R) < 5 or R[0][0] != 1 or R[1][0] != 0:
        return None
    c = 0; i = 0
    while i + 1 < len(R) and R[i][0] == 1 and R[i + 1][0] == 0:
        c += 1; i += 2
    if c < 1:
        return None
    # after the (10)^c block there should be a 0 separator, then 1^d, 0, 1^e
    if i >= len(R) or R[i][0] != 0:
        return None
    i += 1
    d = R[i][1] if i < len(R) and R[i][0] == 1 else 0
    if d:
        i += 1
    if i >= len(R) or R[i][0] != 0:
        return None
    i += 1
    e = R[i][1] if i < len(R) and R[i][0] == 1 else 0
    # left must start with a 1-run of length >= 2 followed by 0 then (10)^p
    if not L or L[0][0] != 1 or L[0][1] < 2:
        return None
    a = L[0][1] - 2
    if a % 2:
        return None
    j = 1
    if j >= len(L) or L[j][0] != 0:
        return None
    j += 1
    p = 0
    while j + 1 < len(L) and L[j][0] == 1 and L[j + 1][0] == 0:
        p += 1; j += 2
    if j < len(L) and L[j][0] != 0:
        return None
    return dict(p=p, a=a, c=c, d=d, e=e)


N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
s = Sim(M)
found = []
for i in range(N):
    if s.halted:
        print('HALT', s.steps); break
    if s.st == 'A':
        c = ce3(s)
        if c is not None:
            found.append((s.steps, c))
            print('Ce3', s.steps, c)
            if len(found) >= 30:
                break
    s.step()
print('done', N, 'macrosteps, steps', s.steps, 'Ce3 hits', len(found))
