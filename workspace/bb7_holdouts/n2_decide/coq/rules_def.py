from common import *
# tape-order builders (left to right); converted to left-side stream order (nearest head first)
def run(blk, v=None, k=0):
    toks = mkrun(blk, {v: 1} if v else {}, 0)
    return toks + list(blk) * k      # tape order: run first, constant copies nearer the right
def a(v=None, k=0): return run((0, 1), v, k)        # (01)^n
def b(v=None, k=0): return run((1, 0), v, k)        # (10)^n
S11 = [1, 1]
def seg(pv, pk, qv, qk): return a(pv, pk) + b(qv, qk)
def ones_sep_seg(v='j', k=0): return run((1, 1, 0, 1, 1, 0), v, k)   # (11 01 10)^n
def ones_seg_sep(v='j', k=0): return run((0, 1, 1, 0, 1, 1), v, k)   # (01 10 11)^n
def to_left(tape, tail):
    out = []
    for t in reversed(tape):
        if isinstance(t, tuple) and t[0] == 'run':
            out.append(('run', tuple(reversed(t[1])), t[2]))
        else:
            out.append(t)
    return pl.norm_side(out + [tail])
def KA(tape, tail=None):
    return ('A', to_left(tape, V('l') if tail is None else tail), [0, 1, BLANK], '>')
RULES = {}
RULES['R1'] = (KA(seg('x', 2, 'y', 0)), KA(seg('x', 0, 'y', 4)))
RULES['R2'] = (KA(seg('p', 1, 'q', 3) + S11 + ones_seg_sep() + seg(None, 1, 'y', 0)),
               KA(seg('p', 1, 'q', 1) + S11 + seg('y', 4, None, 1) + ones_sep_seg()))
RULES['R3'] = (KA(seg('p', 3, None, 1) + S11 + ones_seg_sep() + seg(None, 1, 'y', 0)),
               KA(seg('p', 1, 'y', 4) + ones_sep_seg() + S11 + seg(None, 1, None, 1)))
RULES['R4'] = (KA(ones_seg_sep() + seg(None, 1, 'm', 1) + b('m', 0), BLANK),
               KA(seg(None, 0, None, 1) + ones_sep_seg('j') + ones_sep_seg('m', 1) + S11 + seg(None, 0, None, 3), BLANK))
RULES['R6a'] = (KA(seg('p', 0, 'q', 3) + S11 + ones_seg_sep('j', 1) + seg(None, 0, 'y', 0)),
                KA(seg('p', 0, 'q', 1) + S11 + seg('y', 2, None, 1) + ones_sep_seg('j') + S11 + seg(None, 0, None, 3)))
RULES['R6b'] = (KA(seg('p', 0, 'q', 3) + S11 + seg(None, 0, 'y', 0)),
                KA(seg('p', 0, 'q', 1) + S11 + seg('y', 1, None, 3)))
RULES['R7'] = (KA(seg('p', 2, None, 1) + S11 + ones_seg_sep('j') + seg(None, 0, 'y', 0)),
               KA(seg('p', 0, 'y', 2) + ones_sep_seg('j') + S11 + seg(None, 0, None, 3)))
RULES['R8a'] = (KA(seg(None, 0, None, 1) + S11 + ones_seg_sep('j', 1) + seg(None, 0, 'y', 0), BLANK),
                KA(seg('y', 3, None, 1) + ones_sep_seg('j') + S11 + seg(None, 0, None, 3), BLANK))
RULES['R8b'] = (KA(seg(None, 0, None, 1) + S11 + seg(None, 0, 'y', 0), BLANK),
                KA(seg('y', 2, None, 3), BLANK))
# ---- exhaustion pieces (R4)
def cfg(q, left_tape, right_tape, tail=None, mode='>'):
    L = to_left(left_tape, V('l') if tail is None else tail)
    R = pl.norm_side(list(right_tape) + [BLANK])
    return (q, L, R, mode)
c11 = lambda v=None, k=0: run((1, 1), v, k)
RULES['R4s0'] = (cfg('A', a(None, 1) + b('y'), [0, 1], BLANK), cfg('F', [], a('y', 3) + [0, 0, 1, 1], BLANK))
RULES['R4s1'] = (cfg('A', S11 + a(None, 1) + b('y'), [0, 1]), cfg('A', [], [1, 1] + a('y', 2) + [0, 0, 1, 1]))
RULES['L1'] = (cfg('A', S11 + [0, 1, 1, 0], [1, 1] + a('c') + [0, 0] + c11('n')), cfg('A', [], [1, 1] + a('c') + [0, 0] + c11('n', 3)))
RULES['R4b'] = (cfg('A', [0, 1, 1, 0], [1, 1] + a('c') + [0, 0] + c11('n'), BLANK), cfg('F', [], a('c', 1) + [0, 0] + c11('n', 3), BLANK))
RULES['L2'] = (cfg('F', [], a('c', 3) + [0, 0] + c11('n'), BLANK), cfg('F', [], a('c', 1) + [0, 0] + c11('n', 3), BLANK))
RULES['R4c'] = (cfg('F', [], [0, 1, 0, 1, 0, 0] + c11('n'), BLANK), cfg('A', [0, 1, 0, 1], [0, 0] + c11('n', 2), BLANK))
RULES['L3'] = (cfg('A', [], [0, 0] + c11('n', 4)), cfg('A', [1, 0, 1, 1, 0, 1], [0, 0] + c11('n', 1)))
RULES['R4d'] = (cfg('A', [], [0, 0, 1, 1, 1, 1, 1, 1]), cfg('A', [1, 1, 0, 1, 0, 1, 0], [0, 1]))
RULES['L2a'] = (cfg('F', [], a('c', 3) + [0, 0] + c11('n'), BLANK), cfg('F', [], [0] + b('c', 2) + [0, 1] + c11('n', 1), BLANK))
RULES['L2b'] = (cfg('F', [], [0] + b('c', 2) + [0, 1] + c11('n', 1), BLANK), cfg('F', [], a('c', 1) + [0, 0] + c11('n', 3), BLANK))
RULES['L2b1'] = (cfg('F', [], [0] + b('c', 2) + [0, 1] + c11('n', 1), BLANK), cfg('C', [1, 1], b('c', 1) + [0, 1] + c11('n', 1), BLANK))
RULES['L2b2'] = (cfg('C', [1, 1], b('c', 1) + [0, 1] + c11('n', 1), BLANK), cfg('F', [], a('c', 1) + [0, 0] + c11('n', 3), BLANK))
RULES['L2b2a'] = (cfg('C', [1, 1], b('c', 1) + [0, 1] + c11('n', 1), BLANK), cfg('C', b('c', 1) + [1, 1], [0, 1] + c11('n', 1), BLANK))
RULES['L2b2b'] = (cfg('C', b('c', 1) + [1, 1], [0, 1] + c11('n', 1), BLANK), cfg('F', [], a('c', 1) + [0, 0] + c11('n', 3), BLANK))
def runR(blk, v=None, k=0):
    return list(blk) * k + mkrun(blk, {v: 1} if v else {}, 0)   # constants nearest the head on the right side
aR = lambda v=None, k=0: runR((0, 1), v, k)
bR = lambda v=None, k=0: runR((1, 0), v, k)
c11R = lambda v=None, k=0: runR((1, 1), v, k)
RULES['R4s0'] = (cfg('A', a(None, 1) + b('y'), [0, 1], BLANK), cfg('F', [], aR('y', 3) + [0, 0, 1, 1], BLANK))
RULES['L2'] = (cfg('F', [], aR('c', 3) + [0, 0] + c11R('n'), BLANK), cfg('F', [], aR('c', 1) + [0, 0] + c11R('n', 3), BLANK))
RULES['L2b'] = (cfg('F', [], [0] + bR('c', 2) + [0, 1] + c11R('n', 1), BLANK), cfg('F', [], aR('c', 1) + [0, 0] + c11R('n', 3), BLANK))
RULES['E1'] = (cfg('A', [], [0, 0, 1, 1]), cfg('A', [1, 0], [0, 1]))
RULES['D3O'] = (cfg('A', a('p', 3) + [1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n')),
                cfg('A', a('p', 1) + b('c', 1), [0, 0] + c11R('n', 3)))
RULES['R6s'] = (cfg('A', [1, 1] + b('y'), [0, 1]), cfg('A', [1, 1, 0], [1, 1] + aR('y') + [0, 0, 1, 1, 1, 1, 1, 1]))
RULES['D2E'] = (cfg('A', b('q', 3) + [1, 1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n')),
                cfg('A', b('q', 1) + [1, 1] + a('c') + [0], [0, 0] + c11R('n', 3)))
RULES['D3E'] = (cfg('A', a('p', 1) + [0], [1, 1] + aR('c') + [0, 0] + c11R('n')),
                cfg('A', a('p') + b('c', 2) + [1], [0, 0] + c11R('n', 1)))
RULES['D0E'] = (cfg('A', [1, 0, 1, 1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n'), BLANK),
                cfg('A', a('c') + [0], [0, 0] + c11R('n'), BLANK))
RULES['R6s'] = (cfg('A', [1, 1] + b('y', 1), [0, 1]), cfg('A', [1, 1, 0], [1, 1] + aR('y', 1) + [0, 0, 1, 1, 1, 1, 1, 1]))
RULES['D3E'] = (cfg('A', a('p', 2) + [0], [1, 1] + aR('c') + [0, 0] + c11R('n')),
                cfg('A', a('p', 1) + b('c', 2) + [1], [0, 0] + c11R('n', 1)))
RULES['D0E'] = (cfg('A', [1, 0, 1, 1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n'), BLANK),
                cfg('A', b('c', 1), [0, 0] + c11R('n'), BLANK))
RULES['D3E0'] = (cfg('A', [0, 1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n', 3), BLANK),
                 cfg('A', b('c', 2) + [1], [0, 0] + c11R('n'), BLANK))
RULES['R6s'] = (cfg('A', [0, 1, 1, 0, 1, 1] + b('y', 1), [0, 1]), cfg('A', [0], [1, 1] + aR('y', 1) + [0, 0, 1, 1, 1, 1, 1, 1]))
RULES['D3E'] = (cfg('A', [1, 1] + a('p', 2) + [0], [1, 1] + aR('c') + [0, 0] + c11R('n')),
                cfg('A', [1, 1] + a('p', 1) + b('c', 2) + [1], [0, 0] + c11R('n')))
RULES['D0E'] = (cfg('A', [1, 0, 1, 1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n'), BLANK),
                cfg('A', b('c', 1), [0, 0] + c11R('n', 3), BLANK))
RULES['D3E0'] = (cfg('A', [0, 1, 0], [1, 1] + aR('c') + [0, 0] + c11R('n'), BLANK),
                 cfg('A', b('c', 2) + [1], [0, 0] + c11R('n'), BLANK))
RULES['D3E'] = (cfg('A', [1, 1] + a('p', 2) + [0], [1, 1] + aR('c', 1) + [0, 0] + c11R('n')),
                cfg('A', [1, 1] + a('p', 1) + b('c', 3) + [1], [0, 0] + c11R('n')))
RULES['D3E0'] = (cfg('A', [0, 1, 0], [1, 1] + aR('c', 1) + [0, 0] + c11R('n'), BLANK),
                 cfg('A', b('c', 3) + [1], [0, 0] + c11R('n'), BLANK))
RULES['D3E'] = (cfg('A', [1, 1] + a('p', 2) + [0], [1, 1] + aR('c', 1) + [0, 0] + c11R('n', 1)),
                cfg('A', [1, 1] + a('p', 1) + b('c', 3) + [1], [0, 0] + c11R('n', 1)))
RULES['D3E0'] = (cfg('A', [0, 1, 0], [1, 1] + aR('c', 1) + [0, 0] + c11R('n', 1), BLANK),
                 cfg('A', b('c', 3) + [1], [0, 0] + c11R('n', 1), BLANK))
RULES['D3EL'] = (cfg('A', a('p', 2) + [0], [1, 1] + aR('c', 1) + [0, 0] + c11R('n', 1), BLANK),
                 cfg('A', a('p', 1) + b('c', 3) + [1], [0, 0] + c11R('n', 1), BLANK))
