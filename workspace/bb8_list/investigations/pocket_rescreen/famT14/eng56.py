"""eng56.py: macro engine rows 15/16 (1RB1LG_0RC0LD_1LE0RE_1LC{1RB,0RF}_1RF1RE_0LA0LG_1LH1LA_1LB---), mirrored, event B, z=1.
Coding: unmarked digit v -> run 2v+1, marked v -> run 2v; then 2a, 2b+2. Leading marked zeros are invisible (normalised away).
 R2 d1=(v>0,m): v-1, b'=2b+2 | L0 d1=M0: d1 -> (b+1,0), b'=2
 k>=1 trailing unmarked zeros, x above: R3 x=(v>0): x-1, Z->[b-k,1^(k-1)], b'=4
   RM x=M0 / RB no x: x (or a new top digit) -> M(b-k+1), Z -> [1^(k-1), M2], b'=2"""
def norm(ds):
    i = 0
    while i < len(ds) and ds[i] == (0, 1): i += 1
    return ds[i:]
def step(ds, b):
    ds = norm(list(ds))
    if not ds: return None
    if ds[-1][0] > 0:
        v, m = ds[-1]; ds[-1] = (v - 1, m); return ds, 2 * b + 2, 'R2'
    if ds[-1] == (0, 1):
        ds[-1] = (b + 1, 0); return ds, 2, 'L0'
    k = 0
    while k < len(ds) and ds[-1 - k] == (0, 0): k += 1
    j = len(ds) - 1 - k
    Zm = [(1, 0)] * (k - 1) + [(2, 1)]
    if j >= 0 and ds[j][0] > 0:
        if b - k < 0: return None
        return ds[:j] + [(ds[j][0] - 1, ds[j][1])] + [(b - k, 0)] + [(1, 0)] * (k - 1), 4, 'R3'
    if b - k + 1 < 0: return None
    if j >= 0: return ds[:j] + [(b - k + 1, 1)] + Zm, 2, 'RM'
    return [(b - k + 1, 1)] + Zm, 2, 'RB'
