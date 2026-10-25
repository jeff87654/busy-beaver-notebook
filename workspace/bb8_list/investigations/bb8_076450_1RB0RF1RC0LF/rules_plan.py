"""Planner runs for the rules of 1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---."""
import sys
import planner8 as P
TM = "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---"
P.set_tm(TM)

def run(blk, v, c=0):
    return P.mkrun(blk, {v: 1} if isinstance(v, str) else v, c)

def coq_lin(c, const=0):
    parts = []
    for k, v in c:
        parts.append(k if v == 1 else '%d * %s' % (v, k))
    if const or not parts:
        parts.append(str(const))
    return ' + '.join(parts) if len(parts) > 1 else parts[0]

def m_tloop(cfg):
    """Tloop: l' 1^(3k) (01)^m 0 B>0  -->*  l' (01)^(m+3k) 0 B>0  (stream: [0] (1,0)^m (111)^k ...)."""
    q, L, R, mode = cfg
    if q != 'B' or mode != '>' or R[0] != P.BLANK or L[0] != 0:
        return None
    i = 1; mc = 0; mv = ()
    while True:
        if i + 1 < len(L) and L[i] == 1 and L[i + 1] == 0:
            mc += 1; i += 2
        elif i < len(L) and P.is_run(L[i]) and L[i][1] == (1, 0):
            mv = P.lin_add(mv, L[i][2]); i += 1
        else:
            break
    if not (i < len(L) and P.is_run(L[i]) and L[i][1] == (1, 1, 1)):
        return None
    k = L[i][2]
    newc = P.lin_add(mv, k, 3)
    newL = [0] + P.mkrun((1, 0), newc, mc) + L[i + 1:]
    # rebuild: concrete pairs first then run (mkrun puts const copies first)
    frag = 'follow (Tloop (%s) (%s)).' % (coq_lin(k), coq_lin(mv, mc))
    return ('B', P.norm_side(newL), R, '>'), frag, 'Tloop k=%s m=%s+%d' % (P.cnt_str(k), P.cnt_str(mv), mc)
m_tloop.anytime = True

if __name__ == '__main__':
    X = [1, 1, 1, 0, 1, 1, 1, 0]
    L = [0, 1, 0, 1, 0, 1, 1] + run((1, 1, 1), 'k') + [1, 1] + X + [0, 1, 0] * 5 + [P.V('l')]
    cfg = ('B', L, [P.BLANK], '>')
    script, end = P.drive('P1', cfg, None, matchers=[m_tloop], maxev=200)
