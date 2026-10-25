"""Generate the Coq proof for 1RB0RH_1RC1LE_0LD0RF_---1RE_1LB0LB_1RA0RG_0LC1RF_0LG1LA  (python gen_dl.py OUT.v)"""
import os, sys
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planner8 as pl
from planner8 import BLANK, V, drive, norm_side
from coqgen_util import script_to_coq, crossing_lemma, table
import fam8, pipe
from fam8 import run
from fam8h import X_, Odd_, T3, T4
from fam8d import Xfin

TM = fam8.TM

def cl(t): return '[' + ';'.join(map(str, t)) + ']'

def side_str(side):
    parts = []
    for t in side:
        if isinstance(t, int):
            parts.append('%d >> ' % t)
        elif t == BLANK:
            parts.append('const 0')
        elif t[0] == 'run':
            c = pl.cnt_str(t[2])
            parts.append('%s^^%s *> ' % (cl(t[1]), c if c.isidentifier() else '(%s)' % c))
        else:
            parts.append(t[1])
    return '(' + ''.join(parts) + ')'

def cfg_str(cfg):
    q, L, R, mode = cfg
    assert mode == '>'
    return '%s {{%s}}> %s' % (side_str(L), q, side_str(R))

def vars_of(*cfgs):
    nats, sides = [], []
    for cfg in cfgs:
        for side in (cfg[1], cfg[2]):
            for t in side:
                if isinstance(t, tuple) and t[0] == 'run':
                    for v, _ in t[2]:
                        if v not in nats: nats.append(v)
                elif isinstance(t, tuple) and t[0] == 'VAR':
                    if t[1] not in sides: sides.append(t[1])
    return nats, sides

def wrap(tac):
    body = ''; line = '  '
    for t in tac:
        if len(line) + len(t) > 100:
            body += line.rstrip() + NL; line = '  '
        line += t + ' '
    return body + line.rstrip() + NL

def pipe_lemma(name, lm):
    q, d, xs, ys, c = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['c']
    cs = ''.join('%d >> ' % x for x in c)
    if d == '<':
        stmt = 'forall n l r, %s^^n *> l <{{%s}} %sr -->* l <{{%s}} %s%s^^n *> r' % (cl(xs), q, cs, q, cs, cl(ys))
    else:
        stmt = ('forall n l r, (%sl) {{%s}}> %s^^n *> r -->* (%s%s^^n *> l) {{%s}}> r' % (cs, q, cl(xs), cs, cl(ys), q))
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n' % (name, stmt))

SPECS = []
def spec(name, start, target):
    SPECS.append((name, start, target))

def build_specs():
    SPECS.clear()
    # R1: X(m; S w :: rest) -> X(m+1; w :: rest)
    spec('R1m', X_(0, [0,1,1,run((1,),'y'),0,V('r')]), X_(1, [0,1,run((1,),'y'),0,V('r')]))
    # R3 family (tail T3 = enc (S y :: W))
    spec('ENT3', X_(0, [0,1,run((0,1),'i')]+T3), Odd_(0,0,1,T3,run_c=False))
    spec('CYC3', Odd_(0,0,1,T3), Odd_(1,0,0,T3))
    L=[1,1,1,run((1,1),'c'),BLANK]
    s=('B',norm_side(L),norm_side([0,1,1,1,run((1,1,1,1),'m')]+T3),'>')
    t=Xfin([0,1,run((1,),'y'),0,V('r')])
    spec('FIN3', s, t)
    # R4 family (tail T4 = enc [])
    spec('ENT4', X_(0, [0,1,run((0,1),'i')]+T4), Odd_(0,0,1,T4,run_c=False))
    spec('CYC4', Odd_(0,0,1,T4), Odd_(1,0,0,T4))
    s=('B',norm_side(L),norm_side([0,1,1,1,run((1,1,1,1),'m')]+T4),'>')
    t=('B',norm_side([BLANK]),norm_side([0,0,1,0,1,run((0,1),'c'),0,1,1,1,1,1,run((1,1,1,1),'m'),0,1,BLANK]),'>')
    spec('FIN4', s, t)
    t=('B',[BLANK],norm_side([0,0,1,0,1,1,1,1,1,run((1,1,1,1),'m'),0,1,BLANK]),'>')
    spec('EMP4', X_(0, T4), t)

def gen(outp, init_steps=98):
    pl.set_tm(TM)
    pl.LEMMAS.clear(); pipe.PIPES.clear()
    build_specs()
    bodies = []
    for name, s, t in SPECS:
        script, _ = drive(name, s, t, matchers=[pipe.pipe_matcher()], maxev=400, verbose=False)
        if script[-1][0] != 'end':
            raise SystemExit('planner did not reach target of %s: %r' % (name, script[-3:]))
        nats, sides = vars_of(s, t)
        binders = ' '.join(nats) + (' ' if nats and sides else '') + ' '.join(sides)
        tac = script_to_coq(script, True)
        stmt = 'forall %s%s%s, %s -->+ %s' % (
            (' '.join(nats) + ' ') if nats else '', (' '.join(sides) + ' ') if sides else '', '' , cfg_str(s), cfg_str(t))
        # rewrite "forall a b c , " -> "forall a b c, "
        stmt = stmt.replace(' , ', ', ')
        bodies.append('Lemma %s : %s.\nProof.\n  intros.\n%sQed.\n' % (name, stmt, wrap(tac)))
        nst = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('%-5s literal steps %3d ops %d' % (name, nst, len(script)), file=sys.stderr)
    cross = ''.join(crossing_lemma(nm, pl.LEMMAS[nm]) + NL for nm in sorted(pl.LEMMAS))
    pipes = ''.join(pipe_lemma(nm, pipe.PIPES[nm]) + NL for nm in sorted(pipe.PIPES))
    head = open(os.path.join(HERE, 'head_dl.v.in')).read()
    text = head.replace('@TABLE@', table(TM)).replace('@TM@', TM)
    text = text.replace('@CROSS@', cross).replace('@PIPES@', pipes).replace('@PHASES@', NL.join(bodies))
    text = text.replace('@INIT@', str(init_steps))
    open(outp, 'w', newline=NL).write(text)
    print('wrote', outp, file=sys.stderr)

if __name__ == '__main__':
    gen(sys.argv[1])
