"""Generate the busycoq proof for 1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF (never halts).

usage: python gen_coq.py out.v

Phase lemmas (T1, the six raw rules, Init) are proved by scripts that planner8.py (symbolic execution mirroring
busycoq's [execute]; copied from ../bb8_076450_1RB0RF1RC1RH) writes; pext.py adds sweeps and numeral crossings;
phases.m_TL matches the transfer loop TL (proved by induction from T1). The families, the rule wrappers, the
level step and the final theorem are written below as text.
"""
import sys
import planner8 as P
import pext
import phases as PH
from phases import run, norm, BEX, ALX, XCX, Lv, BL, V

TM = PH.TM
P.set_tm(TM)

RULES = {}
RULES['T1'] = (('B', [0] + run((1, 0), 'b') + [0, 1] + [V('l')], [BL], '>'),
               ('B', [0] + [1, 0] * 4 + run((1, 0), 'b') + [V('l')], [BL], '>'))
RULES['BEraw'] = (BEX([0, 1] * 4 + run((0, 1, 0, 1), 'a'), [1, 0] * 4 + run((1, 0, 1, 0), 'k')),
                  ALX([0, 1] * 2 + run((0, 1, 0, 1), 'a'), [0, 1] * 33 + run((0, 1) * 8, 'k')))
RULES['ALraw'] = (ALX([0, 1] * 4 + run((0, 1, 0, 1), 'a'), [0, 1] * 3 + run((0, 1, 0, 1), 'k')),
                  BEX([0, 1] * 2 + run((0, 1, 0, 1), 'a'), [1, 0] * 24 + run((1, 0) * 8, 'k')))
RULES['AL1raw'] = (ALX([0, 1] * 2, [0, 1] * 3 + run((0, 1, 0, 1), 'k')),
                   XCX([1, 0] * 24 + run((1, 0) * 8, 'k')))
RULES['XCraw'] = (XCX([1, 0] * 4 + run((1, 0, 1, 0), 'j')),
                  Lv([1, 0] * 31 + run((1, 0) * 8, 'j')))
RULES['LVOraw'] = (Lv([1, 0] * 3 + run((1, 0, 1, 0), 'k')),
                   Lv([1, 0] * 18 + run((1, 0) * 8, 'k')))
RULES['LVEraw'] = (Lv([1, 0] * 4 + run((1, 0, 1, 0), 'k')),
                   BEX([0, 1] * 2 + run((0, 1, 0, 1), 'k'), [1, 0] * 10))
ORDER = ['T1', 'BEraw', 'ALraw', 'AL1raw', 'XCraw', 'LVOraw', 'LVEraw']
MATCH = PH.MATCH


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
        if P.is_run(t):
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
            out.append('follow %s.' % op[1])
        elif op[0] == 'align':
            kind, x0, xs, cnt = op[1]
            c = cnt_coq(cnt)
            if kind == 'ALIGN':
                out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
            else:
                # count left as an evar: [rewrite] then matches up to conversion (Sym / sym implicit types)
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


HEAD = r'''(** * BB(8) holdout, subtask 76450: 1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF never halts *)

(** Formalization of [bb8_list/investigations/bb8_076450_1RB0RF1RC0LA.md].
    Generated by gen_coq.py; planner8.py / pext.py mirror [execute] on symbolic tapes.

    Families (tape order, blank outside the word; head position marked):
      Lv N     = E>1 (10)^N 1
      beX x n  = A>0 (01)^(x+1) 1010110111 (10)^n 1
      alX x n  = A>0 (01)^(x+1) 1 (01)^2 1 (01)^(n+2)
      Xc m     = A>0 (01)^3 10111 (10)^m 1
    Rules: beX(2a+3,2k+4) -> alX(2a+1,8k+31), alX(2a+3,2k+1) -> beX(2a+1,8k+24), alX(1,2k+1) -> Xc(8k+24),
    Xc(2j+4) -> Lv(8j+31), Lv(2k+3) -> Lv(8k+18), Lv(2k+4) -> beX(2k+1,10).
    Each rule uses the transfer loop TL, which moves (01) pairs one at a time and writes four (10) pairs per pair.
    The level invariant beX(4i+3, 2n+4) is closed under these rules (see [level_step]). *)

From BB8 Require Import Individual82.
From Coq Require Import Lia PeanoNat.
Set Default Goal Selector "!".

(* machine: 1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, R, B)  | A, 1 => Some (0, R, F)
  | B, 0 => Some (1, R, C)  | B, 1 => Some (0, L, A)
  | C, 0 => Some (0, R, D)  | C, 1 => Some (0, R, B)
  | D, 0 => Some (1, L, E)  | D, 1 => Some (1, R, G)
  | E, 0 => Some (0, L, A)  | E, 1 => Some (0, L, C)
  | F, 0 => Some (0, L, D)  | F, 1 => Some (0, L, G)
  | G, 0 => Some (1, L, H)  | G, 1 => Some (1, R, A)
  | H, 0 => None            | H, 1 => Some (1, L, F)
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

(** ** Tape identities *)

Lemma pow_add : forall (xs : list Sym) a b r, xs^^(a + b) *> r = xs^^a *> xs^^b *> r.
Proof. intros. rewrite lpow_add, Str_app_assoc. reflexivity. Qed.

Lemma p01_2 : forall v r, [0;1;0;1]^^v *> r = [0;1]^^(2 * v) *> r.
Proof.
  induction v; intros.
  - reflexivity.
  - replace (2 * S v) with (S (S (2 * v))) by lia. cbn [lpow app Str_app]. rewrite IHv. reflexivity.
Qed.

Lemma p10_2 : forall v r, [1;0;1;0]^^v *> r = [1;0]^^(2 * v) *> r.
Proof.
  induction v; intros.
  - reflexivity.
  - replace (2 * S v) with (S (S (2 * v))) by lia. cbn [lpow app Str_app]. rewrite IHv. reflexivity.
Qed.

Lemma p01_8 : forall v r, [0;1;0;1;0;1;0;1;0;1;0;1;0;1;0;1]^^v *> r = [0;1]^^(8 * v) *> r.
Proof.
  induction v; intros.
  - reflexivity.
  - replace (8 * S v) with (S (S (S (S (S (S (S (S (8 * v))))))))) by lia.
    cbn [lpow app Str_app]. rewrite IHv. reflexivity.
Qed.

Lemma p10_8 : forall v r, [1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;0]^^v *> r = [1;0]^^(8 * v) *> r.
Proof.
  induction v; intros.
  - reflexivity.
  - replace (8 * S v) with (S (S (S (S (S (S (S (S (8 * v))))))))) by lia.
    cbn [lpow app Str_app]. rewrite IHv. reflexivity.
Qed.
'''

TLOOP = r'''
(** Transfer loop: each pass moves one (01) pair (stream order) and writes four (10) pairs next to the head. *)
Lemma TL : forall m b l,
  (0 >> [1;0]^^b *> [0;1]^^m *> l) {{B}}> const 0 -->* (0 >> [1;0]^^(4 * m + b) *> l) {{B}}> const 0.
Proof.
  induction m; intros.
  - finish.
  - change ([0;1]^^(S m) *> l) with (0 >> 1 >> [0;1]^^m *> l).
    follow T1.
    change (0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> [1;0]^^b *> [0;1]^^m *> l)
      with (0 >> [1;0]^^(4 + b) *> [0;1]^^m *> l).
    replace (4 * S m + b) with (4 * m + (4 + b)) by lia. apply IHm.
Qed.

Lemma TL2 : forall k b l,
  (0 >> [1;0]^^b *> [0;1;0;1]^^k *> l) {{B}}> const 0 -->*
  (0 >> [1;0]^^b *> [1;0;1;0;1;0;1;0;1;0;1;0;1;0;1;0]^^k *> l) {{B}}> const 0.
Proof.
  intros. rewrite p01_2, p10_8, <- pow_add. replace (b + 8 * k) with (4 * (2 * k) + b) by lia. apply TL.
Qed.
'''

TAIL = r'''
(** ** Families *)

Definition Lv (N : nat) : Q * tape := const 0 {{E}}> 1 >> [1;0]^^N *> 1 >> const 0.

Definition beX (x n : nat) : Q * tape :=
  const 0 {{A}}> 0 >> [0;1]^^(x + 1) *> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> 0 >> 1 >> 1 >> 1 >> [1;0]^^n *> 1 >> const 0.

Definition alX (x n : nat) : Q * tape :=
  const 0 {{A}}> 0 >> [0;1]^^(x + 1) *> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> [0;1]^^(n + 2) *> const 0.

Definition Xc (m : nat) : Q * tape :=
  const 0 {{A}}> 0 >> [0;1]^^3 *> 1 >> 0 >> 1 >> 1 >> 1 >> [1;0]^^m *> 1 >> const 0.

(** ** The rules (all parameters) *)

Lemma BE : forall a k, beX (2 * a + 3) (2 * k + 4) -->+ alX (2 * a + 1) (8 * k + 31).
Proof.
  intros. unfold beX, alX.
  replace (2 * a + 3 + 1) with (4 + 2 * a) by lia. replace (2 * k + 4) with (4 + 2 * k) by lia.
  replace (2 * a + 1 + 1) with (2 + 2 * a) by lia. replace (8 * k + 31 + 2) with (33 + 8 * k) by lia.
  rewrite !pow_add, <- !p01_2, <- !p10_2, <- !p01_8.
  apply BEraw.
Qed.

Lemma AL : forall a k, alX (2 * a + 3) (2 * k + 1) -->+ beX (2 * a + 1) (8 * k + 24).
Proof.
  intros. unfold beX, alX.
  replace (2 * a + 3 + 1) with (4 + 2 * a) by lia. replace (2 * k + 1 + 2) with (3 + 2 * k) by lia.
  replace (2 * a + 1 + 1) with (2 + 2 * a) by lia. replace (8 * k + 24) with (24 + 8 * k) by lia.
  rewrite !pow_add, <- !p01_2, <- !p10_8.
  apply ALraw.
Qed.

Lemma AL1 : forall k, alX 1 (2 * k + 1) -->+ Xc (8 * k + 24).
Proof.
  intros. unfold Xc, alX.
  replace (2 * k + 1 + 2) with (3 + 2 * k) by lia. replace (8 * k + 24) with (24 + 8 * k) by lia.
  rewrite !pow_add, <- !p01_2, <- !p10_8.
  apply AL1raw.
Qed.

Lemma XC : forall j, Xc (2 * j + 4) -->+ Lv (8 * j + 31).
Proof.
  intros. unfold Xc, Lv.
  replace (2 * j + 4) with (4 + 2 * j) by lia. replace (8 * j + 31) with (31 + 8 * j) by lia.
  rewrite !pow_add, <- !p10_2, <- !p10_8.
  apply XCraw.
Qed.

Lemma LVO : forall k, Lv (2 * k + 3) -->+ Lv (8 * k + 18).
Proof.
  intros. unfold Lv.
  replace (2 * k + 3) with (3 + 2 * k) by lia. replace (8 * k + 18) with (18 + 8 * k) by lia.
  rewrite !pow_add, <- !p10_2, <- !p10_8.
  apply LVOraw.
Qed.

Lemma LVE : forall k, Lv (2 * k + 4) -->+ beX (2 * k + 1) 10.
Proof.
  intros. unfold Lv, beX.
  replace (2 * k + 4) with (4 + 2 * k) by lia. replace (2 * k + 1 + 1) with (2 + 2 * k) by lia.
  rewrite !pow_add, <- !p10_2, <- !p01_2.
  apply LVEraw.
Qed.

(** ** Levels
    The invariant is Cf (i, n) = beX (4 i + 3) (2 n + 4).
    - i > 0: BE then AL give Cf (i - 1, 16 n + 70).
    - i = 0: BE, AL1, XC, LVO, LVE give Cf (128 n + 591, 3): the (10) pairs of the counter become the next
      level's (01) pairs.  Every parameter keeps the parity its rule needs, so no level ending ever halts. *)

Definition Cf (p : nat * nat) : Q * tape := let '(i, n) := p in beX (4 * i + 3) (2 * n + 4).

Lemma level_step : forall p, exists p', Cf p -->+ Cf p'.
Proof.
  intros [i n]. destruct i as [| i].
  - exists (128 * n + 591, 3). unfold Cf; cbv beta iota.
    eapply progress_trans. { apply (BE 0 n). }
    replace (8 * n + 31) with (2 * (4 * n + 15) + 1) by lia.
    eapply progress_trans. { apply (AL1 (4 * n + 15)). }
    replace (8 * (4 * n + 15) + 24) with (2 * (16 * n + 70) + 4) by lia.
    eapply progress_trans. { apply (XC (16 * n + 70)). }
    replace (8 * (16 * n + 70) + 31) with (2 * (64 * n + 294) + 3) by lia.
    eapply progress_trans. { apply (LVO (64 * n + 294)). }
    replace (8 * (64 * n + 294) + 18) with (2 * (256 * n + 1183) + 4) by lia.
    replace (4 * (128 * n + 591) + 3) with (2 * (256 * n + 1183) + 1) by lia.
    apply (LVE (256 * n + 1183)).
  - exists (i, 16 * n + 70). unfold Cf; cbv beta iota.
    replace (4 * S i + 3) with (2 * (2 * i + 2) + 3) by lia.
    eapply progress_trans. { apply (BE (2 * i + 2) n). }
    replace (2 * (2 * i + 2) + 1) with (2 * (2 * i + 1) + 3) by lia.
    replace (8 * n + 31) with (2 * (4 * n + 15) + 1) by lia.
    replace (2 * (16 * n + 70) + 4) with (8 * (4 * n + 15) + 24) by lia.
    replace (4 * i + 3) with (2 * (2 * i + 1) + 1) by lia.
    apply (AL (2 * i + 1) (4 * n + 15)).
Qed.

(** ** From the blank tape to the family: 234 steps to Lv 10, then LVE gives beX 7 10 = Cf (1%nat, 3%nat). *)

Lemma init_reach : c0 -->* Lv 10.
Proof. unfold Lv. do 234 step. finish. Qed.

Theorem nonhalt : ~ halts tm c0.
Proof.
  apply multistep_nonhalt with (Cf (1%nat, 3%nat)).
  - eapply evstep_trans. { apply init_reach. }
    apply progress_evstep. apply (LVE 3).
  - apply progress_nonhalt_simple with (C := Cf) (i0 := (1%nat, 3%nat)).
    apply level_step.
Qed.
'''


def main():
    outp = sys.argv[1]
    P.LEMMAS.clear()
    pext.SWEEPS.clear()
    bodies = {}
    for nm in ORDER:
        start, tgt = RULES[nm]
        start, tgt = norm(start), norm(tgt)
        ms = [pext.m_concrete, pext.m_sweep] if nm == 'T1' else MATCH
        script, _ = P.drive(nm, start, tgt, matchers=ms, maxev=3000, verbose=False)
        assert script[-1][0] == 'end', (nm, script[-1])
        rel = '-->*' if nm == 'T1' else '-->+'
        bodies[nm] = lemma_text(nm, start, tgt, script, rel)
        print('%-7s literal steps %6d, ops %d' % (nm, nsteps(script), len(script)), file=sys.stderr)
    text = HEAD
    text += ('\n(** ** Crossing a run of blocks (generated; blocks in stream order, nearest the head first;\n'
             '    the literal cells before [l] / [r] are context that is read and restored) *)\n\n')
    for nm in sorted(P.LEMMAS):
        text += crossing_lemma(nm, P.LEMMAS[nm]) + '\n'
    text += '(** ** Sweeps whose small context travels with the head (generated) *)\n\n'
    for nm in sorted(pext.SWEEPS):
        text += pext.sweep_lemma(nm, pext.SWEEPS[nm]) + '\n'
    text += '(** ** One transfer pass and the transfer loop *)\n\n' + bodies['T1'] + TLOOP + '\n'
    text += '(** ** Raw rules (scripts generated by the planner) *)\n\n'
    for nm in ORDER[1:]:
        text += bodies[nm] + '\n'
    text += TAIL
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, len(P.LEMMAS), 'crossings', len(pext.SWEEPS), 'sweeps', file=sys.stderr)


if __name__ == '__main__':
    main()
