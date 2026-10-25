"""Generate the busycoq non-halting proof for 1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA.

usage: python gen_coq.py out.v

Phase lemmas R1, R0o, T1, T2 are proved by scripts written by planner8.py (symbolic execution that mirrors
busycoq's [execute]); the sweep lemmas swF<n> are matched by the custom matcher swF below.
The families, the wrappers, the counter step and the final theorem are written below as text.
Helpers (cl, side_coq, cfg_coq, script_to_coq, crossing_lemma, lemma_text) adapted from
../bb8_076450_1RB0RF1RC0LA/gen_coq.py.
"""
import sys
import planner8 as P
from planner8 import mkrun, V, BLANK, is_run, norm_side
from lit import Sim

TM = "1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA"
P.set_tm(TM)
BL = BLANK
S3 = (1, 1, 1)
S6 = (1,) * 6
Z6 = (0, 1, 0, 1, 0, 1)

SWF = set()


def swF(cfg):
    """F moving right over a run of 1-blocks with a 0 (hole) behind it: 0 F> 1^k -> 1^k 0 F>."""
    q, L, R, mode = cfg
    if q == 'F' and mode == '>' and L[0] == 0 and is_run(R[0]) and all(x == 1 for x in R[0][1]):
        blk = R[0][1]
        SWF.add(len(blk))
        return ((q, norm_side([0, ('run', blk, R[0][2])] + L[1:]), R[1:], '>'),
                'follow swF%d.' % len(blk), 'swF')
    return None


def D(L):
    return ('D', L, [BL], '>')


RULES = {
    # X 0 1^(3m+1) 00 D>  ->  X 1^(3m+6) 00 D>          (X arbitrary, never read)
    'R1': (D([0, 0] + mkrun(S3, {'m': 1}) + [1, 0, V('l')]),
           D([0, 0] + mkrun(S3, {'m': 1}) + [1] * 6 + [V('l')])),
    # X 0 1^(6i+3) 00 D>  ->  X 1 (10)^(3i+2) 1 00 D>    (X arbitrary, never read)
    'R0o': (D([0, 0] + mkrun(S6, {'i': 1}) + [1, 1, 1, 0, V('l')]),
            D([0, 0, 1] + mkrun(Z6, {'i': 1}) + [0, 1, 0, 1, 1, V('l')])),
    # 0^inf 1^(6i+4) 00 D>  ->  0^inf 1 (10)^(3i+5) 1 00 D>      (R1, then R0o)
    'T1': (D([0, 0] + mkrun(S6, {'i': 1}) + [1, 1, 1, 1, BL]),
           D([0, 0, 1] + mkrun(Z6, {'i': 1}) + [0, 1] * 5 + [1, BL])),
    # 0^inf 1^(6j+2) 00 D>  ->  0^inf 1 (10)^(3j+1) 11 (10)^2 1 00 D>
    'T2': (D([0, 0] + mkrun(S6, {'j': 1}) + [1, 1, BL]),
           D([0, 0, 1, 0, 1, 0, 1, 1, 1] + mkrun(Z6, {'j': 1}) + [0, 1, 1, BL])),
}
ORDER = ['R1', 'R0o', 'T1', 'T2']


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def cnt_coq(c):
    assert len(c) == 1 and c[0][1] == 1, c
    return c[0][0]


def side_coq(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append('%d >> ' % t)
        elif t == BL:
            out.append('const 0')
        elif t[0] == 'VAR':
            out.append(t[1])
        else:
            out.append('%s^^%s *> ' % (cl(t[1]), cnt_coq(t[2])))
    return ''.join(out)


def paren(s):
    return s if s == 'const 0' or s.isidentifier() else '(' + s + ')'


def cfg_coq(cfg):
    q, L, R, mode = cfg
    if mode == '>':
        return '%s {{%s}}> %s' % (paren(side_coq(L)), q, paren(side_coq(R)))
    return '%s <{{%s}} %s' % (paren(side_coq(L)), q, paren(side_coq(R)))


def vars_of(cfg):
    q, L, R, mode = cfg
    vs = []
    for t in L + R:
        if is_run(t):
            v = cnt_coq(t[2])
            if v not in vs:
                vs.append(v)
        elif isinstance(t, tuple) and t[0] == 'VAR' and t[1] not in vs:
            vs.append(t[1])
    return vs


def script_to_coq(script, plus):
    out = []
    first = True
    for op in script:
        if op[0] == 'steps':
            n = op[1]
            if first and plus:
                assert n >= 1, 'a -->+ lemma must start with a literal step'
                out.append('step1.')
                n -= 1
            first = False
            if n:
                out.append('do %d step.' % n)
            continue
        assert not (first and plus), 'a -->+ lemma must start with a literal step'
        first = False
        if op[0] == 'cross':
            out.extend(['follow %s.' % op[1]] * op[2])
        elif op[0] == 'align':
            kind, x0, xs, cnt = op[1]
            c = cnt_coq(cnt)
            if kind == 'ALIGN':
                out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
            else:
                out.append('rewrite (align_lpow_const %d %s _). simpl app.' % (x0, cl(xs)))
        elif op[0] == 'lemma':
            out.append(op[1])
        elif op[0] == 'end':
            if op[1]:
                out.append('do %d step.' % op[1])
            out.append('finish_norm.')
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return out


def crossing_lemma(name, lm):
    q, d, xs, ys, ctx = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['ctx']
    ctxs = ''.join('%d >> ' % c for c in ctx)
    if d == '>':
        stmt = 'forall n l r, %sl {{%s}}> %s^^n *> r -->* %s^^n *> %sl {{%s}}> r' % (ctxs, q, cl(xs), cl(ys), ctxs, q)
    else:
        stmt = 'forall n l r, %s^^n *> l <{{%s}} %sr -->* l <{{%s}} %s^^n *> %sr' % (cl(xs), q, ctxs, q, cl(ys), ctxs)
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n'
            % (name, stmt))


def swf_lemma(k):
    ones = cl((1,) * k)
    return ('Lemma swF%d : forall n l r, (0 >> l) {{F}}> (%s^^n *> r) -->* (0 >> %s^^n *> l) {{F}}> r.\n'
            'Proof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n' % (k, ones, ones))


def lemma_text(name, start, tgt, script, rel):
    vs = vars_of(start)
    for v in vars_of(tgt):
        if v not in vs:
            vs.append(v)
    head = 'forall %s, ' % ' '.join(vs) if vs else ''
    stmt = '%s%s %s %s' % (head, cfg_coq(start), rel, cfg_coq(tgt))
    tac = script_to_coq(script, rel == '-->+')
    body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt)
    line = '  '
    for t in tac:
        if len(line) + len(t) > 110:
            body += line.rstrip() + '\n'
            line = '  '
        line += t + ' '
    body += line.rstrip() + '\nQed.\n'
    return body


def nsteps(script):
    return sum(o[1] for o in script if o[0] in ('steps', 'end'))


def table(tms):
    rows = []
    for qi, ch in enumerate(tms.split('_')):
        q = 'ABCDEFGH'[qi]
        ents = []
        for s in (0, 1):
            e = ch[3 * s:3 * s + 3]
            if e == '---':
                ents.append('| %s, %d => None' % (q, s))
            else:
                ents.append('| %s, %d => Some (%s, %s, %s)' % (q, s, e[0], e[1], e[2]))
        rows.append('  ' + '  '.join('%-24s' % x for x in ents).rstrip())
    return '\n'.join(rows)


def init_steps():
    """Steps from the blank tape to Cc 2 2 = 0^inf 1 (10)^2 11 (10)^2 1 0 0 D> 0^inf (literal)."""
    s = Sim(TM, size=4096)
    want = [1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0]
    for _ in range(100000):
        if not s.step():
            raise RuntimeError('halted')
        p = s.pos
        if s.state == 3 and not any(s.tape[:p - len(want)]) and list(s.tape[p - len(want):p]) == want \
                and not any(s.tape[p:]):
            return s.steps
    raise RuntimeError('init config not reached')


HEAD = r'''(** * BB(8) holdout, subtask 76450: %(tm)s never halts *)

(** Formalization of [bb8_list/investigations/bb8_076450_1RB0LC0RC0RF.md].
    Generated by gen_coq.py; planner8.py mirrors [execute] on symbolic tapes.

    All configurations have the head in state D on the right edge, after two blank cells:
      0^inf W 0 0 D> 0^inf.
    Rules (X arbitrary and never read):
      R1  : X 0 1^(3m+1) 00 D>  -->+  X 1^(3m+6) 00 D>
      R0o : X 0 1^(6i+3) 00 D>  -->+  X 1 (10)^(3i+2) 1 00 D>
      T1  : 0^inf 1^(6i+4) 00 D>  -->+  0^inf 1 (10)^(3i+5) 1 00 D>            (R1 then R0o)
      T2  : 0^inf 1^(6j+2) 00 D>  -->+  0^inf 1 (10)^(3j+1) 11 (10)^2 1 00 D>
    Family:
      Cc a k = 0^inf 1 (10)^a 11 (10)^k 1 00 D>
      Dc a i = 0^inf 1 (10)^a 1^(6i+3) 00 D>          (= Cc a 0 after 6i more ones)
      Cc a k      -->* Dc a k                (R1 applied k times: each (10) pair adds five 1s)
      Dc (a+1) i  -->+ Dc a (3i+2)           (R0o, then R1 applied 3i+2 times)
      Dc 0 i      -->+ Dc (9i+16) 2          (T1, R1 applied 3i+5 times, T2, R1 twice)
    The only undefined transition D1 would need 1^n with n = 2 mod 3 behind a 0 that is not the blank
    left end; the family never produces it.  The blank tape reaches Cc 2 2 after %(init)d steps,
    so the machine never halts. *)

From BB8 Require Import Individual82.
From Coq Require Import Lia PeanoNat.
Set Default Goal Selector "!".

(* machine: %(tm)s *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
%(table)s
  end.

Notation "c --> c'" := (c -[ tm ]-> c')   (at level 40).
Notation "c -->* c'" := (c -[ tm ]->* c') (at level 40).
Notation "c -->+ c'" := (c -[ tm ]->+ c') (at level 40).

(** ** Tape normalization (as in BB7_16582_1RB1LD.v) *)

Lemma align_lpow : forall (x : Sym) xs ys n,
  (x::xs)^^n *> x >> ys = x >> (xs ++ [x])^^n *> ys.
Proof.
  induction n.
  - reflexivity.
  - simpl. repeat rewrite Str_app_assoc. rewrite IHn. reflexivity.
Qed.

Lemma align_lpow_const : forall (x : Sym) xs n,
  (x::xs)^^n *> const x = x >> (xs ++ [x])^^n *> const x.
Proof. intros. rewrite const_unfold at 1. apply align_lpow. Qed.

Ltac align_tape := repeat ((rewrite align_lpow || rewrite align_lpow_const); simpl app).
Ltac norm_nat := repeat progress (rewrite ?Nat.add_succ_r, ?Nat.add_0_r; simpl).
Ltac finish_norm := apply evstep_refl'; norm_nat; align_tape; try reflexivity; lia_refl.
Ltac step1 := eapply progress_intro; [prove_step | simpl_tape].

(** ** Crossing a run of blocks (generated; blocks in stream order, nearest the head first) *)

'''

TAIL = r'''
(** ** Tape identities *)

Lemma three_S : forall m r, [1;1;1]^^m *> 1 >> 1 >> 1 >> r = [1;1;1]^^(S m) *> r.
Proof.
  induction m; intros.
  - reflexivity.
  - simpl. rewrite IHm. reflexivity.
Qed.

Lemma three_S2 : forall m r,
  [1;1;1]^^m *> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> r = [1;1;1]^^(S (S m)) *> r.
Proof. intros. rewrite three_S, three_S. reflexivity. Qed.

Lemma six_three : forall n r, [1;1;1;1;1;1]^^n *> r = [1;1;1]^^(n + n) *> r.
Proof.
  induction n; intros.
  - reflexivity.
  - rewrite Nat.add_succ_r. simpl. rewrite IHn. reflexivity.
Qed.

Lemma zo_tail : forall j k r,
  [0;1;0;1;0;1]^^j *> [0;1]^^k *> r = [0;1]^^(3 * j + k) *> r.
Proof.
  induction j; intros.
  - reflexivity.
  - replace (3 * S j + k) with (S (S (S (3 * j + k)))) by lia.
    simpl. rewrite IHj. reflexivity.
Qed.

Lemma zo1 : forall j r, [0;1;0;1;0;1]^^j *> 0 >> 1 >> r = [0;1]^^(3 * j + 1) *> r.
Proof. intros. rewrite <- (zo_tail j 1 r). reflexivity. Qed.

Lemma zo2 : forall j r, [0;1;0;1;0;1]^^j *> 0 >> 1 >> 0 >> 1 >> r = [0;1]^^(3 * j + 2) *> r.
Proof. intros. rewrite <- (zo_tail j 2 r). reflexivity. Qed.

Lemma zo5 : forall j r,
  [0;1;0;1;0;1]^^j *> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> r = [0;1]^^(3 * j + 5) *> r.
Proof. intros. rewrite <- (zo_tail j 5 r). reflexivity. Qed.

(** ** R1 applied once per (10) pair: each pair adds five 1s *)

Lemma R1iter : forall k m l,
  (0 >> 0 >> [1;1;1]^^m *> 1 >> [0;1]^^k *> l) {{D}}> const 0 -->*
  (0 >> 0 >> [1;1;1]^^(m + k + k) *> 1 >> l) {{D}}> const 0.
Proof.
  induction k; intros.
  - rewrite !Nat.add_0_r. finish.
  - change ([0;1]^^(S k) *> l) with (0 >> 1 >> [0;1]^^k *> l).
    eapply evstep_trans; [apply progress_evstep, R1 |].
    rewrite three_S2.
    follow (IHk (S (S m)) l). finish.
Qed.

(** ** The configuration family *)

Definition Cc (a k : nat) : Q * tape :=
  (0 >> 0 >> 1 >> [0;1]^^k *> 1 >> 1 >> [0;1]^^a *> 1 >> const 0) {{D}}> const 0.

Definition Dc (a i : nat) : Q * tape :=
  (0 >> 0 >> [1;1;1;1;1;1]^^i *> 1 >> 1 >> 1 >> [0;1]^^a *> 1 >> const 0) {{D}}> const 0.

(** Inner counter: (10)^k 1 -> 1^(6k+1). *)
Lemma C_D : forall a k, Cc a k -->* Dc a k.
Proof.
  intros. unfold Cc, Dc.
  follow (R1iter k 0 (1 >> 1 >> [0;1]^^a *> 1 >> const 0)).
  rewrite six_three. finish.
Qed.

(** Outer digit: one (10) pair of the outer counter is consumed and the inner counter k -> 3k+2. *)
Lemma Dstep : forall a i, Dc (S a) i -->+ Dc a (3 * i + 2).
Proof.
  intros. unfold Dc.
  change ([0;1]^^(S a) *> 1 >> const 0) with (0 >> 1 >> [0;1]^^a *> 1 >> const 0).
  eapply progress_evstep_trans; [apply R0o |].
  rewrite zo2.
  apply (C_D a (3 * i + 2)).
Qed.

(** Outer counter exhausted: 0^inf 1^(6i+4) -> ... -> Dc (9i+16) 2. *)
Lemma Dtop : forall i, Dc 0 i -->+ Dc (9 * i + 16) 2.
Proof.
  intros. unfold Dc.
  change ([0;1]^^0 *> 1 >> const 0) with (1 >> const 0).
  eapply progress_evstep_trans; [apply T1 |].
  rewrite zo5.
  follow (R1iter (3 * i + 5) 0 (1 >> const 0)).
  replace (0 + (3 * i + 5) + (3 * i + 5)) with ((3 * i + 5) + (3 * i + 5)) by lia.
  rewrite <- six_three.
  eapply evstep_trans; [apply progress_evstep, T2 |].
  rewrite zo1.
  replace (3 * (3 * i + 5) + 1) with (9 * i + 16) by lia.
  apply (C_D (9 * i + 16) 2).
Qed.

(** ** Reaching the family from the blank tape *)

Lemma init_reach : c0 -->* Cc 2 2.
Proof. unfold Cc. do %(init)d step. finish. Qed.

(** ** Non-halting *)

Theorem nonhalt : ~ halts tm c0.
Proof.
  apply multistep_nonhalt with (Dc 2 2).
  - eapply evstep_trans; [apply init_reach | apply C_D].
  - change (Dc 2 2) with ((fun p : nat * nat => Dc (fst p) (snd p)) (2, 2)).
    apply progress_nonhalt_simple.
    intros [[| a] i]; simpl.
    + exists (9 * i + 16, 2). apply Dtop.
    + exists (a, 3 * i + 2). apply Dstep.
Qed.
'''


def main():
    outp = sys.argv[1]
    P.LEMMAS.clear()
    bodies = []
    for nm in ORDER:
        start, tgt = RULES[nm]
        script, _ = P.drive(nm, start, tgt, matchers=(swF,), maxev=400, verbose=False)
        if not script or script[-1][0] != 'end':
            raise RuntimeError('phase %s did not reach its target' % nm)
        bodies.append(lemma_text(nm, start, tgt, script, '-->+'))
        print('%-4s literal steps %4d, ops %d' % (nm, nsteps(script), len(script)), file=sys.stderr)
    subst = dict(tm=TM, table=table(TM), init=init_steps())
    text = HEAD % subst
    for nm in sorted(P.LEMMAS):
        text += crossing_lemma(nm, P.LEMMAS[nm]) + '\n'
    for k in sorted(SWF):
        text += swf_lemma(k) + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += TAIL % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(P.LEMMAS), 'crossing lemmas and', len(SWF), 'sweep lemmas', file=sys.stderr)


if __name__ == '__main__':
    main()
