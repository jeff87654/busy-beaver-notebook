"""eng34.py: macro engine for rows 3/4 (1RB1LG_0RC0RD_1LC0RE_---0RH_1RF1RE_1LH0LG_1LH1LA_{0RA0LA,1LH0LA}), mirrored, event state A, z=2.
State at a=0: (ds, b), ds = [(v, mark)] top->bottom; tape runs = [2v+mark ...] + [0 (a), 2b+2], trailing zeros 2.
Macro step (next a=0 state):
 R2  d1=(v>0,m): v-1; b' = 2b+4                      (a = b+2)
 k = # trailing unmarked zeros (k>=1 case), x = digit above them, y = digit above x
   no x            : REBUILD ds' = [P=(0,1), (2,1), (1,0)^(b-1)]; b' = 2   (a=1)
   x=(v>0,m)       : x -> (v-1,m); Z -> [(b-k+2,0)] + [(1,0)]^(k-1); b' = 2
   x=(0,1), y      : y run += 1 (merge), x removed; Z -> [(b-k+1,1)] + [(1,0)]^(k-1); b' = 2
   x=(0,1), no y   : keep x; Z -> [(b-k+1,1)] + [(1,0)]^(k-1); b' = 2
 k=0, d1=(0,1):    y: merge (y run += 1, d1 removed), b' = 2b+3 ; no y ([M0] alone): b' = 2b+3 (loop)"""
def rmerge(y):
    r = 2 * y[0] + y[1] + 1
    return (r // 2, r % 2)
def step(ds, b):
    ds = list(ds)
    if ds and ds[-1][0] > 0:
        v, m = ds[-1]; ds[-1] = (v - 1, m); return ds, 2 * b + 4, 'R2'
    if ds and ds[-1] == (0, 1):
        if len(ds) >= 2:
            y = ds[-2]; return ds[:-2] + [rmerge(y)], 2 * b + 3, 'M0low-merge'
        return ds, 2 * b + 3, 'M0-alone'
    k = 0
    while k < len(ds) and ds[-1 - k] == (0, 0): k += 1
    j = len(ds) - 1 - k
    if j < 0:
        if b < 1: return None
        return [(0, 1), (2, 1)] + [(1, 0)] * (b - 1), 2, 'REBUILD'
    x = ds[j]
    if x[0] > 0:
        if b - k + 2 < 0: return None
        return ds[:j] + [(x[0] - 1, x[1])] + [(b - k + 2, 0)] + [(1, 0)] * (k - 1), 2, 'R3'
    if b - k + 1 < 0: return None
    Z = [(b - k + 1, 1)] + [(1, 0)] * (k - 1)
    if j >= 1:
        return ds[:j - 1] + [rmerge(ds[j - 1])] + Z, 2, 'merge'
    return ds[:j + 1] + Z, 2, 'top-M0'
