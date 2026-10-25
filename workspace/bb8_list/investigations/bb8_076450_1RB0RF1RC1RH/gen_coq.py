"""Generate the busycoq halting proof for 1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---.

usage: python gen_coq.py out.v

Phase lemmas are proved by scripts that planner8.py (symbolic execution mirroring busycoq's [execute]; copied from
../bb8_076450_1RB0RF1RC0LF and extended with a halting stop and a loop stop) writes. pext.py adds sweeps and numeral
crossings; loops.py matches the two transfer loops TAloop / TBloop (proved by induction from the one-pass lemmas
TA1 / TB1). The rest (families N and Lv, the cycle, the iteration, the level transitions and the final theorem) is
written below as text.
"""
import sys
import planner8 as P
import pext
import loops

TM = "1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF---"
P.set_tm(TM)
BL = P.BLANK
V = P.V


def run(blk, v):
    return [('run', tuple(blk), ((v, 1),))]


def norm(cfg):
    q, L, R, mode = cfg
    return (q, P.norm_side(list(L)), P.norm_side(list(R)), mode)


# left contexts (stream order, nearest the blocks first), after the cell 0 that N / Lv write explicitly
L1 = [0, 0, 1, 0, 1, 0, 1, 1]                                  # tape 1 1010100 (+0) : level-1 prefix "1 10101000"
L2 = [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1]             # tape 11010010 1010100 (+0)
HR = [0, 1, 0, 0, BL]     # H> 0100   (right side of N)
FR = [1, 0, 0, 0, BL]     # F> 1000   (right side of the TA loop)
LR = [1, 1, 0, 1, BL]     # F> 1101   (right side of Lv)

PH = {}      # name -> (start, target, target_override_coq or None)
PH['TA1'] = (('F', run((0, 1, 0, 1), 'n') + [0, 0, 1, 0, 1, 0, 1, 0, V('l')], FR, '>'),
             ('F', [0, 1, 0, 1] * 6 + run((0, 1, 0, 1), 'n') + [0, 0, 1, 0, V('l')], FR, '>'), None)
PH['TB1'] = (('H', run((1, 0, 1, 0), 'm') + [0, 1, 0, 1, V('l')], HR, '>'),
             ('H', [1, 0, 1, 0] * 6 + run((1, 0, 1, 0), 'm') + [V('l')], HR, '>'), None)
PH['M1'] = (('H', run((1, 0, 1, 0), 'm') + [0, 1, 1, 0] * 3 + [V('l')], HR, '>'),
            ('F', [0, 1, 0, 1] * 3 + [0, 0, 1, 0] + [1, 0, 1, 0] * 4 + run((1, 0, 1, 0), 'm') + [0, 1, 1, 0] + [V('l')],
             FR, '>'), None)
PH['M2'] = (('F', run((0, 1, 0, 1), 'n') + [0, 0, 1, 0] + [0, 1, 1, 0] + [0, V('l')], FR, '>'),
            ('H', [1, 0, 1, 0] * 3 + [0, 1, 0, 1] * 7 + run((0, 1, 0, 1), 'n') + [0, V('l')], HR, '>'), None)
PH['Start'] = (('F', [0] + [1, 1, 0, 0] * 5 + [V('l')], LR, '>'),
               ('H', [1, 0, 1, 0] * 279 + [0, V('l')], HR, '>'),
               '[1;0;1;0]^^279 *> 0 >> l {{H}}> 0 >> 1 >> const 0')
PH['End1'] = (('H', run((1, 0, 1, 0), 'm') + [0] + L1 + [BL], HR, '>'),
              ('F', [0, 1, 1, 0, 0] + run((1, 1, 0, 0), 'm') + L2 + [BL], LR, '>'), None)
PH['Init'] = (('A', [BL], [BL], '>'),
              ('F', [0] + [1, 1, 0, 0] * 11 + L1 + [BL], LR, '>'), None)

FOLD = 40
MATCH = [loops.m_rot, loops.m_TA, loops.m_TB, pext.m_concrete, pext.m_sweep]


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


def script_to_coq(script):
    out = []
    for op in script:
        if op[0] == 'steps':
            if op[1]:
                out.append('do %d step.' % op[1])
        elif op[0] == 'cross':
            out.append('follow %s.' % op[1])
        elif op[0] == 'align':
            kind, x0, xs, cnt = op[1]
            c = cnt_coq(cnt)
            if kind == 'ALIGN':
                out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
            else:
                out.append('rewrite (align_lpow_const %d %s %s). simpl app.' % (x0, cl(xs), c))
        elif op[0] == 'lemma':
            f = op[1]
            if isinstance(f, tuple):
                kind, k, n = f
                out.append('follow (%sloop %s %s).' % (kind, k, n))
            else:
                out.append(f)
        elif op[0] in ('end', 'halt', 'stop'):
            if op[1]:
                out.append('do %d step.' % op[1])
            out.append('finish_norm.')
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return out


def lemma_text(name, start, tgt, script, tgt_override=None, extra_vars=()):
    vs = vars_of(start)
    for v in vars_of(tgt) if tgt_override is None else ():
        if v not in vs:
            vs.append(v)
    for v in extra_vars:
        if v not in vs:
            vs.append(v)
    tgt_s = tgt_override if tgt_override else cfg_coq(tgt)
    head = 'forall %s, ' % ' '.join(vs) if vs else ''
    stmt = '%s%s -->* %s' % (head, cfg_coq(start), tgt_s)
    tac = script_to_coq(script)
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
    return sum(o[1] for o in script if o[0] in ('steps', 'end', 'halt', 'stop'))


def plain_phase(name):
    start, tgt, ov = PH[name]
    start, tgt = norm(start), norm(tgt)
    ms = MATCH if name in ('Start', 'End1', 'Init') else [pext.m_concrete, pext.m_sweep]
    script, _ = P.drive(name, start, tgt, matchers=ms, maxev=3000, verbose=False)
    assert script[-1][0] == 'end', (name, script[-1])
    print('%-6s literal steps %6d, ops %d' % (name, nsteps(script), len(script)), file=sys.stderr)
    return lemma_text(name, start, tgt, script, ov)


# ---------------------------------------------------------------- the halting phase, cut at symbolic loops
def lin_coq(c, sub):
    """linear form (tuple of (var, coeff)) -> Coq string, substituting variables by Coq expressions"""
    parts = []
    for v, a in c:
        e = sub[v]
        parts.append('(%s)' % e if a == 1 else '%d * (%s)' % (a, e))
    return ' + '.join(parts)


def chain(prefix, start, target, params):
    """Drive from start to target ('HALT' or a config), cutting at every transfer loop. Each loop output becomes
    the start of the next segment, with at most two concrete blocks and a fresh variable for the rest, so that
    long concrete runs never appear in the Coq terms. Returns (segment lemma texts, composite proof lines,
    final config, substitution)."""
    loops.STOP_ALL = True
    seg = norm(start)
    sub = dict(params)
    texts, comp = [], []
    final = None
    ct = P.canon(norm(target)) if target != 'HALT' else None
    for it in range(40):
        name = '%s%d' % (prefix, it)
        script, e = P.drive(name, seg, target if target == 'HALT' else norm(target), matchers=MATCH, maxev=3000,
                            verbose=False)
        last = script[-1]
        svars = [v for v in vars_of(seg) if v in sub and sub[v] != v or v.startswith('n')]
        nontrivial = any(o[0] in ('cross', 'align', 'lemma') for o in script) or nsteps(script) > 0
        if nontrivial:
            texts.append(lemma_text(name, seg, e, script))
            vs = vars_of(seg)
            while vs and not (vs[-1] in sub and sub[vs[-1]] != vs[-1]):
                vs = vs[:-1]          # trailing variables are left to unification
            args = ' '.join('(%s)' % sub[v] if (v in sub and sub[v] != v) else '_' for v in vs)
            comp.append('follow (%s %s).' % (name, args) if args else 'follow %s.' % name)
            print('%-6s literal steps %6d, ops %d, end %s' % (name, nsteps(script), len(script), last[0]),
                  file=sys.stderr)
        if last[0] in ('halt', 'end'):
            final = e
            comp.append('finish.')
            break
        assert last[0] == 'stop', (name, last)
        kind, kstr, mstr, m0, mr, k0, kr, i, j = last[2]
        q, L, R, mode = e
        K = ' + '.join([str(k0)] + (['(%s)' % lin_coq(kr, sub)] if kr else []))
        Mx = ' + '.join([str(m0)] + (['(%s)' % lin_coq(mr, sub)] if mr else []))
        comp.append('follow (%sloop (%s) (%s)).' % (kind, K, Mx))
        blk = (0, 1, 0, 1) if kind == 'TA' else (1, 0, 1, 0)
        conc = m0 + 6 * k0
        sym = []
        if mr:
            sym.append('(%s)' % lin_coq(mr, sub))
        if kr:
            sym.append('6 * (%s)' % lin_coq(kr, sub))
        rest = ([0, 0, 1, 0] + L[j:]) if kind == 'TA' else L[j:]
        if ct is not None and not sym:
            full = norm((q, [x for _ in range(conc) for x in blk] + rest, R, mode))
            if P.canon(full) == ct:
                comp.append('finish.')
                final = full
                break
        keep = conc if conc <= FOLD else 2
        newL = [x for _ in range(keep) for x in blk]
        if conc - keep or sym:
            fresh = 'n%s%d' % (prefix.lower(), it)
            expr = ' + '.join(([str(conc - keep)] if conc - keep else []) + sym)
            sub[fresh] = expr
            newL += run(blk, fresh)
            comp.append('replace ((%s) + 6 * (%s)) with (%d + (%s)) by lia.' % (Mx, K, keep, expr))
        else:
            comp.append('replace ((%s) + 6 * (%s)) with %d by lia.' % (Mx, K, keep))
        seg = norm((q, newL + rest, R, mode))
    loops.STOP_ALL = False
    assert final is not None
    return texts, comp, final, sub


def subst_cfg_coq(cfg, sub):
    fin = cfg_coq(cfg)
    for v in sorted(vars_of(cfg), key=len, reverse=True):
        if v in sub and sub[v] != v:
            fin = fin.replace('^^%s ' % v, '^^(%s) ' % sub[v])
    return fin


def halt_phase():
    start = ('H', run((1, 0, 1, 0), 'm') + [0, 1, 1, 0, 0, 1, 1, 0, 0] + L2 + [BL], HR, '>')
    texts, comp, final, sub = chain('Hs', start, 'HALT', {'m': 'm'})
    fin = subst_cfg_coq(final, sub)
    return texts, fin, comp


HEAD = r'''(** * BB(8) holdout, subtask 76450: 1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF--- HALTS *)

(** Formalization of [bb8_list/investigations/bb8_076450_1RB0RF1RC1RH.md]. Generated by gen_coq.py.
    Families (tape order; [l] is the part of the tape left of the blocks, never visited by the cycle):
      N x m l  = l (0011)^x 0 (0101)^m H>0100        (head in state H on the 0 of 0100, blank beyond)
      Lv X l   = l (0011)^X 0 F>1101                 (head in state F on the first 1 of 1101)
    Rules:
      Ncyc   : N (3+x) m l -->* N x (36m+207) l      (three blocks pay for two x6 transfers)
      StartL : Lv (5+x) l  -->* N x 279 l
      End1   : N 0 m l1    -->* Lv (1+m) l2          (level 1 ends: the counter becomes the next level's blocks)
      HaltN  : N 2 m l2    -->* H reading 1          (a level-2 ending with two blocks left halts;
                                                       the final tape has exactly 72m + 394 ones)
    Run: blank -> Lv 11 l1 -> N 6 279 l1 -> N 0 (G 2 279) l1 -> Lv (1 + G 2 279) l2, and G 2 279 = 3(q+2),
    so Lv (5 + (3q+2)) l2 -> N (3q+2) 279 l2 -> N 2 (G q 279) l2 -> halt, q = 12 G 1 279 + 67 = 123079.
    G is never evaluated. sigma = 72 G(123079,279) + 394 = (717984 * 36^123079 - 1114)/35 ~ 2.93e191552. *)

From BB8 Require Import Individual82.
From Coq Require Import Lia PeanoNat.
Set Default Goal Selector "!".

(* machine: 1RB0RF_1RC1RH_0RD0RG_1LE0RB_0LA0LC_0LD0RA_1RD0LB_0RF--- *)
Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, R, B)  | A, 1 => Some (0, R, F)
  | B, 0 => Some (1, R, C)  | B, 1 => Some (1, R, H)
  | C, 0 => Some (0, R, D)  | C, 1 => Some (0, R, G)
  | D, 0 => Some (1, L, E)  | D, 1 => Some (0, R, B)
  | E, 0 => Some (0, L, A)  | E, 1 => Some (0, L, C)
  | F, 0 => Some (0, L, D)  | F, 1 => Some (0, R, A)
  | G, 0 => Some (1, R, D)  | G, 1 => Some (0, L, B)
  | H, 0 => Some (0, R, F)  | H, 1 => None
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

Lemma rot4 : forall (a b c d : Sym) n r, a >> [b;c;d;a]^^n *> r = [a;b;c;d]^^n *> a >> r.
Proof. intros. symmetry. apply (align_lpow a [b;c;d]). Qed.
'''

LOOPS = r'''
(** ** The two transfer loops (each pass moves one block and adds six) *)

Lemma TAloop : forall k n l,
  [0;1;0;1]^^n *> 0 >> 0 >> 1 >> 0 >> [1;0;1;0]^^k *> l {{F}}> 1 >> const 0 -->*
  [0;1;0;1]^^(n + 6 * k) *> 0 >> 0 >> 1 >> 0 >> l {{F}}> 1 >> const 0.
Proof.
  induction k; intros.
  - finish.
  - follow (TA1 n ([1;0;1;0]^^k *> l)). follow (IHk (6 + n) l). finish.
Qed.

Lemma TBloop : forall k m l,
  [1;0;1;0]^^m *> [0;1;0;1]^^k *> l {{H}}> 0 >> 1 >> const 0 -->*
  [1;0;1;0]^^(m + 6 * k) *> l {{H}}> 0 >> 1 >> const 0.
Proof.
  induction k; intros.
  - finish.
  - follow (TB1 m ([0;1;0;1]^^k *> l)). follow (IHk (6 + m) l). finish.
Qed.
'''

FAM = r'''
(** ** Families, the cycle and its iteration *)

Definition N (x m : nat) (l : side) : Q * tape :=
  [1;0;1;0]^^m *> 0 >> [1;1;0;0]^^x *> l {{H}}> 0 >> 1 >> const 0.

Definition Lv (X : nat) (l : side) : Q * tape :=
  0 >> [1;1;0;0]^^X *> l {{F}}> 1 >> 1 >> 0 >> 1 >> const 0.

Lemma Ncyc : forall x m l, N (3 + x) m l -->* N x (36 * m + 207) l.
Proof.
  intros. unfold N.
  follow (M1 m (0 >> [1;1;0;0]^^x *> l)).
  follow (TAloop (4 + m) 3).
  follow (M2 (3 + 6 * (4 + m)) ([1;1;0;0]^^x *> l)).
  follow (TBloop (7 + (3 + 6 * (4 + m))) 3).
  finish.
Qed.

Fixpoint G (k m : nat) : nat :=
  match k with
  | O => m
  | S k' => 36 * G k' m + 207
  end.

Lemma Niter : forall k x m l, N (3 * k + x) m l -->* N x (G k m) l.
Proof.
  induction k; intros.
  - finish.
  - replace (3 * S k + x) with (3 * k + (3 + x)) by lia.
    follow (IHk (3 + x) m l). apply Ncyc.
Qed.

Lemma StartL : forall x l, Lv (5 + x) l -->* N x 279 l.
Proof. intros. unfold Lv, N. apply (Start ([1;1;0;0]^^x *> l)). Qed.

Definition l1 : side := 0 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> const 0.
Definition l2 : side := 0 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 1 >> 1 >> const 0.

Lemma End1L : forall m, N 0 m l1 -->* Lv (1 + m) l2.
Proof. intros. unfold N, Lv, l1, l2. apply End1. Qed.

Lemma InitL : c0 -->* Lv 11 l1.
Proof. unfold Lv, l1. apply Init. Qed.
'''


def main():
    outp = sys.argv[1]
    P.LEMMAS.clear()
    pext.SWEEPS.clear()
    bodies = {}
    for nm in ['TA1', 'TB1', 'M1', 'M2', 'End1', 'Init']:
        bodies[nm] = plain_phase(nm)
    st_start, st_tgt, st_ov = PH['Start']
    stexts, scomp, _, _ = chain('St', st_start, st_tgt, {'l': 'l'})
    sbody = 'Lemma Start : forall l, %s -->* %s.\nProof.\n  intros.\n' % (cfg_coq(norm(st_start)), st_ov)
    for c in scomp:
        sbody += '  ' + c + '\n'
    sbody += 'Qed.\n'
    bodies['Start'] = '\n'.join(stexts) + '\n' + sbody
    htexts, hfin_coq, hcomp = halt_phase()
    text = HEAD
    text += ('\n(** ** Crossing a run of blocks (generated; blocks in stream order, nearest the head first;\n'
             '    the literal cells before [l] / [r] are context that is read and restored) *)\n\n')
    import gen_lemmas
    for nm in sorted(P.LEMMAS):
        text += gen_lemmas.crossing_lemma(nm, P.LEMMAS[nm]) + '\n'
    text += '(** ** Sweeps whose small context travels with the head (generated) *)\n\n'
    for nm in sorted(pext.SWEEPS):
        text += pext.sweep_lemma(nm, pext.SWEEPS[nm]) + '\n'
    text += '(** ** One transfer pass (generated) *)\n\n' + bodies['TA1'] + '\n' + bodies['TB1']
    text += LOOPS
    text += '\n(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    for nm in ['M1', 'M2', 'Start', 'End1', 'Init']:
        text += bodies[nm] + '\n'
    text += '(** ** The halting ending (segments between transfer loops, generated) *)\n\n'
    for t in htexts:
        text += t + '\n'
    text += FAM
    text += '\n(** ** Halting from N 2 m l2 *)\n\n'
    text += 'Lemma HaltN : forall m, N 2 m l2 -->* %s.\nProof.\n  intros. unfold N, l2.\n' % hfin_coq
    for c in hcomp:
        text += '  ' + c + '\n'
    text += 'Qed.\n'
    import re
    text += TAIL.replace('@FINALG@', re.sub(r'\bm\b', '(G (12 * G 1 279 + 67) 279)', hfin_coq))
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, len(P.LEMMAS), 'crossings', len(pext.SWEEPS), 'sweeps', file=sys.stderr)


TAIL = r'''
(** ** Halting *)

Lemma G_S : forall k m, G (S k) m = 36 * G k m + 207.
Proof. reflexivity. Qed.

Opaque G.

Theorem halt : halts tm c0.
Proof.
  (* level 1: Lv 11 l1 -> N 6 279 l1 -> N 0 (G 2 279) l1 -> Lv (1 + G 2 279) l2 *)
  (* G 2 279 = 36 G 1 279 + 207 = 3 (q + 2) with q = 12 G 1 279 + 67, so level 2 has 3q + 2 + 5 blocks *)
  assert (Hrun : c0 -->* @FINALG@).
  { follow InitL.
    follow (StartL 6 l1).
    follow (Niter 2 0 279 l1).
    follow (End1L (G 2 279)).
    replace (1 + G 2 279) with (5 + (3 * (12 * G 1 279 + 67) + 2)) by (rewrite (G_S 1 279); lia).
    follow (StartL (3 * (12 * G 1 279 + 67) + 2) l2).
    follow (Niter (12 * G 1 279 + 67) 2 279 l2).
    apply HaltN. }
  destruct (with_counter Hrun) as [n Hn].
  eapply halts_multistep; [| exact Hn].
  apply halted_halts. reflexivity.
Qed.
'''

if __name__ == '__main__':
    main()
