"""Generate phase lemmas (planner scripts) for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF."""
import sys
sys.path.insert(0, '.')
import planner8 as pl
from planner8 import *
from kk import U
import coqgen_util as cg

TM = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF"
pl.set_tm(TM)
Z = (1, 0, 1)


def R(v, blk=(1, 0)):
    return ('run', tuple(blk), lin({v: 1}))


def VL():
    return V('l')


def cnt_coq(c):
    parts = []
    for k, v in c:
        parts.append(k if v == 1 else '%d * %s' % (v, k))
    return '(' + ' + '.join(parts) + ')'


def side2coq(side):
    out = ''
    for t in side:
        if isinstance(t, int):
            out += '%d >> ' % t
        elif t == BLANK:
            return out + 'const 0'
        elif t[0] == 'VAR':
            return out + t[1]
        else:
            out += '[%s]^^%s *> ' % (';'.join(map(str, t[1])), cnt_coq(t[2]))
    raise RuntimeError('no terminator')


def cfg2coq(cfg):
    q, Lf, Rt, mode = cfg
    if mode == '>':
        return '(%s) {{%s}}> (%s)' % (side2coq(Lf), q, side2coq(Rt))
    return '(%s) <{{%s}} (%s)' % (side2coq(Lf), q, side2coq(Rt))


def varnames(*cfgs):
    names = set()
    for cfg in cfgs:
        for side in (cfg[1], cfg[2]):
            for t in side:
                if isinstance(t, tuple) and t[0] == 'VAR':
                    names.add(t[1])
                if isinstance(t, tuple) and t[0] == 'run':
                    for k, v in t[2]:
                        names.add(k)
    return sorted(names)


def tac_of(script, progress):
    out = []
    i = 0
    first = True
    while i < len(script):
        op = script[i]
        if op[0] == 'halt':
            if op[1] > 0:
                out.append('do %d step.' % op[1])
            out.append('apply evstep_refl.')
            i += 1
            first = False
            continue
        if op[0] == 'steps':
            nxt = script[i + 1]
            exact = nxt[0] == 'lemma' or True
            if first and progress:
                if op[1] == 0:
                    raise RuntimeError('progress phase must start with a literal step')
                out.append('eapply progress_intro; [prove_step | simpl_tape].')
                if op[1] > 1:
                    out.append('do %d step.' % (op[1] - 1))
            else:
                if op[1] > 0:
                    out.append('do %d step.' % op[1])
            first = False
            if nxt[0] == 'cross':
                out.extend(['follow %s.' % nxt[1]] * nxt[2])
            elif nxt[0] == 'align':
                kind, x0, xs, cnt = nxt[1]
                c = pl.cnt_str(cnt)
                if '+' in c or not c.isidentifier():
                    raise RuntimeError('align on composite count %r' % (cnt,))
                cl = cg.cl(xs)
                if kind == 'ALIGN':
                    out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl, c))
                else:
                    out.append('rewrite (align_lpow_const %d %s %s). simpl app.' % (x0, cl, c))
            else:
                raise RuntimeError('unexpected %r' % (nxt,))
            i += 2
        elif op[0] == 'end':
            if first and progress:
                out.append('start_progress.')
                first = False
            out.append('do %d step. finish_norm.' % op[1])
            i += 1
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return out


def wrap(tacs):
    body = ''
    line = '  '
    for t in tacs:
        if len(line) + len(t) > 100:
            body += line.rstrip() + '\n'
            line = '  '
        line += t + ' '
    return body + line.rstrip() + '\n'


PH = {}


def add(name, start, target=None):
    PH[name] = (start, target)


add('ROUND', ('G', [R('T'), 1, 1, 0, R('N'), 1, VL()], [BLANK], '>'),
    ('G', [1, 0, 1, 0, R('T'), 1, R('N'), 1, VL()], [BLANK], '>'))
add('R1F', ('G', U(4, 'T') + [1, 1] + [1, 0] * 3 + [R('A'), 1, VL()], [BLANK], '>'),
    ('G', [1, 0, 1, 0, 1] + U(7, 'T') + [1, R('A'), 1, VL()], [BLANK], '>'))
add('R2F', ('G', U(4, 'T') + [1, 1] + U(1) + [1] + U(3, 'X') + [1, VL()], [BLANK], '>'),
    ('G', U(2) + [1] + U(1) + [1] + U(7, 'T') + [1] + U(0, 'X') + [1, VL()], [BLANK], '>'))
add('E3', ('G', [R('T')] + [1, 1] + U(1) + [1] + [1, 0, 1] + [R('M', Z), VL()], [BLANK], '>'),
    ('C', [R('T'), 1, 0, 1, 1] + [R('M', Z), VL()], [0, 1, 0, 1, 1, 0, 1, 0, BLANK], '<'))
add('HOP', ('C', [R('T'), 1, 0, 1, 1] + [1, 0, 1] + [R('M', Z), VL()], [0, 1, 0, 1, R('j', Z), 0, BLANK], '<'),
    ('C', [R('T'), 1, 0, 1, 1] + [R('M', Z), VL()], [0, 1, 0, 1, 1, 0, 1, R('j', Z), 0, BLANK], '<'))
add('X3', ('C', [R('T'), 1, 0, 1, 1] + U(3, 'X') + [1, VL()], [0, 1, 0, 1, 1, 0, 1, R('J', Z), 0, BLANK], '<'),
    ('G', U(2) + [1] + U(1) + [1] + U(1) + [1] + [R('J', Z)] + U(3, 'T') + [1] + U(0, 'X') + [1, VL()], [BLANK], '>'))


def Q0():
    return [1, 0, 0, 1, 0, 0, 1, R('J', (0, 0, 1)), 0, 1, 0, BLANK]


add('X4', ('C', [R('T'), 1, 0, 1, 1, BLANK], [0, 1, 0, 1, 1, 0, 1, R('J', Z), 0, BLANK], '<'),
    ('C', [R('T', (0, 1)), 1, 1, BLANK], [1, 0, 1] * 6 + Q0(), '<'))
add('TLP', ('C', [0, 1, R('T', (0, 1)), 1, 1, BLANK], [R('t', Z)] + Q0(), '<'),
    ('C', [R('T', (0, 1)), 1, 1, BLANK], [1, 0, 1, 1, 0, 1, R('t', Z)] + Q0(), '<'))
add('FIN', ('C', [1, 1, BLANK], [1, 0, 1] * 5 + [R('t', Z)] + Q0(), '<'), None)


def gen(names=None):
    pl.LEMMAS.clear()
    bodies = []
    for name, (st, tg) in PH.items():
        if names and name not in names:
            continue
        script, c = drive(name, st, tg, maxev=400, verbose=False)
        last = script[-1]
        halting = last[0] == 'halt'
        if tg is not None and last[0] != 'end':
            raise SystemExit('%s: did not reach target: %r' % (name, script[-3:]))
        if tg is None and not halting:
            raise SystemExit('%s: not halting: %r' % (name, script[-3:]))
        nm = varnames(st, tg) if tg else varnames(st)
        if halting:
            stmt = 'forall %s, exists c, %s -->* c /\\ halted tm c' % (' '.join(nm), cfg2coq(st))
            tac = tac_of(script, False)
            body = ('Lemma %s : %s.\nProof.\n  intros. eexists. split.\n  - ' % (name, stmt)
                    + wrap(tac).lstrip() + '  - simpl. reflexivity.\nQed.\n')
        elif script[0] == ('steps', 0):
            stmt = 'forall %s, %s -->* %s' % (' '.join(nm), cfg2coq(st), cfg2coq(tg))
            tac = tac_of(script, False)
            body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt) + wrap(tac) + 'Qed.\n'
        else:
            stmt = 'forall %s, %s -->+ %s' % (' '.join(nm), cfg2coq(st), cfg2coq(tg))
            if len(script) == 1 and script[0][0] == 'end':
                tac = ['eapply progress_intro; [prove_step | simpl_tape].', 'do %d step. finish_norm.' % (script[0][1] - 1)]
            else:
                tac = tac_of(script, True)
            body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt) + wrap(tac) + 'Qed.\n'
        bodies.append(body)
        print('%-6s ops %d' % (name, len(script)), file=sys.stderr)
    cross = ''.join(cg.crossing_lemma(nm, pl.LEMMAS[nm]) + '\n' for nm in sorted(pl.LEMMAS))
    return cross, '\n'.join(bodies)


if __name__ == '__main__':
    cross, ph = gen()
    open('phases35.v', 'w', newline='\n').write('(** crossings *)\n' + cross + '(** phases *)\n' + ph)
    print('wrote phases35.v')
