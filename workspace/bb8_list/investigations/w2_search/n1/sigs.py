"""sigs.py: n1 period signature and chains (shared by genum5/dropslot)."""
def sig(toks):
    """'P 2^x 5 1^m 0 0 45 1^z | a r' -> (P, x, m, z) or None"""
    d = toks[:-2]
    z = 0
    while z < len(d) and d[len(d) - 1 - z] == 1: z += 1
    i = len(d) - 1 - z
    if i < 3 or d[i] != 45 or d[i-1] != 0 or d[i-2] != 0: return None
    j = i - 3; m = 0
    while j >= 0 and d[j] == 1: m += 1; j -= 1
    if j < 0 or d[j] != 5: return None
    j -= 1; x = 0
    while j >= 0 and d[j] == 2: x += 1; j -= 1
    if x == 0: return None
    return (tuple(d[:j+1]), x, m, z)

def chains(sigs):
    """sigs: list of (stage, P, x, m, z); returns list of chains [start_stage, end_stage, m0, m_end, length, z0, z_end]"""
    out = []; cur = None
    for s, P, x, m, z in sigs:
        if cur and P == cur[7] and x == cur[8] + 4 and m == cur[3] - 14:
            cur[1] = s; cur[3] = m; cur[4] += 1; cur[6] = z; cur[8] = x
        else:
            if cur: out.append(cur)
            cur = [s, s, m, m, 1, z, z, P, x]
    if cur: out.append(cur)
    return out

