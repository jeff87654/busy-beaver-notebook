"""Generate proofs/BB8_193804_1RB0RH.v  (python gen193.py OUT.v)"""
import os, sys
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planner8 as pl
from planner8 import BLANK
from coqgen_util import script_to_coq, table
import fam, pipe
from chain import chain

TM = fam.TM
KNEAR = 1

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
    if mode == '>':
        return '%s {{%s}}> %s' % (side_str(L), q, side_str(R))
    return '%s <{{%s}} %s' % (side_str(L), q, side_str(R))

def pipe_lemma(name, lm):
    q, d, xs, ys, c = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['c']
    cs = ''.join('%d >> ' % x for x in c)
    if d == '<':
        stmt = 'forall n l r, %s^^n *> l <{{%s}} %sr -->* l <{{%s}} %s%s^^n *> r' % (cl(xs), q, cs, q, cs, cl(ys))
    else:
        stmt = ('forall n l r, (%sl) {{%s}}> %s^^n *> r -->* (%s%s^^n *> l) {{%s}}> r' % (cs, q, cl(xs), cs, cl(ys), q))
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n' % (name, stmt))

def wrap(tac):
    body = ''; line = '  '
    for t in tac:
        if len(line) + len(t) > 100:
            body += line.rstrip() + NL; line = '  '
        line += t + ' '
    return body + line.rstrip() + NL

def gen(outp, k=KNEAR):
    pl.set_tm(TM)
    pipe.PIPES.clear()
    rounds = chain(k)
    assert len(rounds) == 10 and all(r[3] for r in rounds)
    names = {}
    lemmas = []
    # collect pipe names in order
    for nm, s, t, sc in rounds:
        for op in sc:
            if op[0] == 'lemma':
                lname = op[1].split()[1].rstrip('.')
                if lname not in names:
                    names[lname] = 'pp%d' % (len(names) + 1)
    plem = ''.join(pipe_lemma(names[n], pipe.PIPES[n]) + NL for n in names)
    rl = []
    for i, (nm, s, t, sc) in enumerate(rounds):
        tac = script_to_coq(sc, True)
        tac = [ ' '.join((names[x.split()[1].rstrip('.')] if x.startswith('follow pp_') else x) if False else x for x in [t_]) for t_ in tac]
        tac = [('follow %s.' % names[t_.split()[1].rstrip('.')]) if t_.startswith('follow pp_') else t_ for t_ in tac]
        start = fam.family(s[0], s[1], 0, s[2]); tgt = fam.family(t[0], t[1], 0, t[2])
        rl.append('Lemma round%d : forall n, %s -->+ %s.\nProof.\n  intros.\n%sQed.\n' % (i, cfg_str(start), cfg_str(tgt), wrap(tac)))
        print('round', i, nm, 'lit steps', sum(o[1] for o in sc if o[0] in ('steps', 'end')), file=sys.stderr)
    fam0 = fam.family('B', k, 0, 0)
    famtxt = cfg_str(fam0)
    cyc = 'Lemma cycle : forall n, Fam n -->+ Fam (S n).\nProof.\n  intros. unfold Fam.\n'
    for i in range(9):
        cyc += '  eapply progress_trans; [apply round%d |].\n' % i
    cyc += '  apply round9.\nQed.\n'
    head = open(os.path.join(HERE, 'head193.v.in')).read()
    text = head.replace('@TABLE@', table(TM)).replace('@TM@', TM).replace('@FAM@', famtxt)
    text = text.replace('@PIPES@', plem).replace('@ROUNDS@', NL.join(rl)).replace('@CYCLE@', cyc)
    open(outp, 'w', newline=NL).write(text)
    print('wrote', outp, file=sys.stderr)

if __name__ == '__main__':
    gen(sys.argv[1])
