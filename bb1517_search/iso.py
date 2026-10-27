from tm import parse

CORE = '1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_0LK1RJ_1RE0LA_1RA0RF_1LH1LA_1RB1RM'
TNF = '1LB1LA_1RC0LA_1RD1RC_1RE1RK_1RF0LJ_0LG1RI_1RE0RH_1LF0RC_1RM0LE_1LA1LE_0LL1LB_0RM1LL_1RZ1RH'


def iso(a, b):
    A, B = parse(a), parse(b)
    n = len(A)
    assert len(B) == n
    # find bijection by backtracking on transition structure
    mapping = {}
    inv = {}
    order = [0]
    res = []

    def rec(i):
        if i == n:
            res.append(dict(mapping)); return True
        s = order[i]
        if s in mapping:
            return rec(i + 1)
        for t in range(n):
            if t in inv:
                continue
            ok = True
            for sym in (0, 1):
                ta, tb = A[s][sym], B[t][sym]
                ha = ta is None or ta[2] == 'Z'
                hb = tb is None or tb[2] == 'Z'
                if ha or hb:
                    if not (ha and hb):
                        ok = False; break
                    continue
                if (ta[0], ta[1]) != (tb[0], tb[1]):
                    ok = False; break
                ns = ord(ta[2]) - 65
                nt = ord(tb[2]) - 65
                if ns in mapping and mapping[ns] != nt:
                    ok = False; break
                if nt in inv and inv[nt] != ns:
                    ok = False; break
            if not ok:
                continue
            mapping[s] = t; inv[t] = s
            if rec(i + 1):
                return True
            del mapping[s]; del inv[t]
        return False

    # BFS order by transitions
    seen = {0}; q = [0]
    while q:
        s = q.pop(0)
        for sym in (0, 1):
            t = A[s][sym]
            if t is not None and t[2] != 'Z':
                ns = ord(t[2]) - 65
                if ns not in seen:
                    seen.add(ns); q.append(ns)
    order = list(seen)
    if len(order) < n:
        order += [i for i in range(n) if i not in seen]
    if rec(0):
        return res[0]
    return None


if __name__ == '__main__':
    m = iso(CORE, TNF)
    print(m)
    if m:
        print('core -> TNF:', ''.join(chr(65 + m[i]) for i in range(len(m))))
