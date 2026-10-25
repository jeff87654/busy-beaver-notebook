"""Planner phases for 1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF."""
import sys
import planner8 as P
import pext
TM = "1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF"
P.set_tm(TM)
BL = P.BLANK; V = P.V

def run(blk, v): return [('run', tuple(blk), ((v, 1),))]
def norm(cfg):
    q, L, R, mode = cfg
    return (q, P.norm_side(list(L)), P.norm_side(list(R)), mode)

def take_pairs(L, i, pair):
    """concrete copies of pair at L[i:], then optional run whose block is pair repeated; returns (conc, run_tok or None, newi)"""
    c = 0
    while L[i:i+2] == list(pair):
        c += 1; i += 2
    rt = None
    if i < len(L) and P.is_run(L[i]) and len(L[i][1]) % 2 == 0 and L[i][1] == tuple(pair) * (len(L[i][1]) // 2):
        rt = L[i]; i += 1
    return c, rt, i

LOOPLOG = []
def m_TL(cfg):
    """Transfer loop (Coq TL, TL1, TL2):
       0 >> [1;0]^^b *> [0;1]^^m *> l {{B}}> const 0 -->* 0 >> [1;0]^^(4*m+b) *> l {{B}}> const 0
       destination b concrete; source: concrete (0,1) pairs, then optionally one run of (0,1)^j blocks (consumed fully)."""
    q, L, R, mode = cfg
    if q != 'B' or mode != '>' or R != [BL] or L[0] != 0:
        return None
    b0, brt, i = take_pairs(L, 1, (1, 0))
    if brt is not None:
        return None
    m0, mrt, j = take_pairs(L, i, (0, 1))
    if m0 == 0 and mrt is None:
        return None
    rest = L[j:]
    frags = []
    if m0:
        frags.append('follow (TL %d %d).' % (m0, b0))
    bb = b0 + 4 * m0
    if mrt is not None:
        blk = mrt[1]; jj = len(blk) // 2
        cnt = mrt[2]
        assert len(cnt) == 1 and cnt[0][1] == 1
        v = cnt[0][0]
        frags.append('follow (TL%d %s %d).' % (jj, v, bb))
        newL = [0] + [1, 0] * bb + [('run', (1, 0) * (4 * jj), cnt)] + rest
    else:
        newL = [0] + [1, 0] * bb + rest
    LOOPLOG.append((b0, m0, mrt))
    return (q, P.norm_side(newL), R, mode), ' '.join(frags), 'TL b=%d m0=%d run=%s' % (b0, m0, mrt and P.cnt_str(mrt[2]))
m_TL.anytime = True

MATCH = [m_TL, pext.m_concrete, pext.m_sweep]

def w(s):
    return [int(c) for c in s]

# configurations (head at the left edge; left blank)
def Lv(Rbody):            # E reading 1, right: 1 (10)^N 1
    return ('E', [BL], [1] + Rbody + [1, BL], '>')
def AL(Abody, nbody):     # A reading 1: 1 (01)^A 1010110101 (01)^n
    return ('A', [BL], [1] + Abody + w('1010110101') + nbody + [BL], '>')
def BE(Abody, nbody):     # A reading 1: 1 (01)^A 1010110111 (10)^n 1
    return ('A', [BL], [1] + Abody + w('1010110111') + nbody + [1, BL], '>')
def XC(mbody):            # A reading 1: 1010110111 (10)^m 1
    return ('A', [BL], w('1010110111') + mbody + [1, BL], '>')

PH = {}
PH['T1'] = (('B', [0] + run((1,0),'b') + [0,1] + [V('l')], [BL], '>'),
            ('B', [0] + [1,0]*4 + run((1,0),'b') + [V('l')], [BL], '>'))

if __name__ == '__main__':
    import json
    names = sys.argv[1:] or list(PH)
    for nm in names:
        start, tgt = PH[nm]
        try:
            script, end = P.drive(nm, norm(start), norm(tgt), matchers=MATCH, maxev=3000, verbose=True)
            print('  END:', P.show(end))
        except Exception as e:
            import traceback; traceback.print_exc()

# X-forms: 4 steps after the "event" (head in A on the blank two cells left of the word; the word's first 1 is kept)
def ALX(Abody1, nbody2):  # [A:0] (01)^(A+1) 1 (01)^2 1 (01)^(n+2)
    return ('A', [BL], [0] + Abody1 + [1] + [0,1]*2 + [1] + nbody2 + [BL], '>')
def BEX(Abody1, nbody):   # [A:0] (01)^(A+1) 1010110111 (10)^n 1
    return ('A', [BL], [0] + Abody1 + w('1010110111') + nbody + [1, BL], '>')

def XCX(mbody):           # [A:0] (01)^3 10111 (10)^m 1   (4 steps after [A:1] 010110111 (10)^m 1 ... see notes)
    return ('A', [BL], [0] + [0,1]*3 + w('10111') + mbody + [1, BL], '>')

LOG = []
def m_log(cfg):
    q, L, R, mode = cfg
    if (mode == '<' and L[0] == BL) or (mode == '>' and L == [BL]):
        LOG.append(cfg)
    return None
m_log.anytime = True

def trydrive(name, start, tgt, maxev=3000, log=False):
    LOG.clear()
    ms = ([m_log] if log else []) + MATCH
    script, end = P.drive(name, norm(start), norm(tgt) if tgt else None, matchers=ms, maxev=maxev, verbose=False)
    ok = script[-1][0] == 'end'
    print('%-6s %s ops=%d steps=%d' % (name, 'OK' if ok else 'FAIL '+repr(script[-1]), len(script),
          sum(o[1] for o in script if o[0] in ('steps', 'end'))))
    if not ok or log:
        for c in LOG: print('   edge:', P.show(c)[:220])
        print('   END:', P.show(end)[:300])
    return script, end
