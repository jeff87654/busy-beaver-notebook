"""Assemble ONE self-contained Coq file for the BB(10) candidate n1
   1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC

  python gen_selfcontained_n1.py [OUT.v]     (default: BB10_n1_selfcontained.v next to this script)

Adapted from gen_selfcontained.py (the BB(9) record file; that script is unchanged).  The output depends only on the
Coq standard library (tested with Coq 8.20.1):
  * busycoq's core (LibTactics, Helper, TM, Compute, Flip, Permute, Individual; commit bd2e36f, MIT) is inlined
    verbatim, each file wrapped in a module `BusyCoq_<File>` that is then `Export`ed;
  * BB102.v / Individual102.v (the 10-state instantiation) follow, at top level;
  * Module Champion10: the BB(10) champion's halting proof and exact score (BB10_champion_1RB1RA.v, _bound.v);
  * Module Lead10: the 10-state candidate 0LJ0LC (BB10_lead_1RB0RA.v, BB10_lead_bound.v) and its comparison with
    the champion (BB10_lead_vs_champion.v);
  * Module N1: n1's halting proof (BB10_n1.v) and score files (BB10_n1_bound.v, BB10_n1_exact.v, BB10_n1_fgh.v);
  * a final section restating the main results with one `ones` predicate for the three machines.
n1 is wrapped in a module too: BB10_n1.v (like BB10_lead_1RB0RA.v) defines a function `F`, which in the multi-file
build shadowed the imported state constructor F; at the top level of one file it would be a duplicate name.
Edits besides the BB(9) ones (Require lines hoisted or turned into Import, Print Assumptions collected at the end,
`Local Open Scope sym_scope` at the start of each inlined file, St_H behind `Notation H := St_H`), now ALL
state constructors St_A..St_J and busycoq's dir constructors St_L, St_R behind abbreviations A..J, L, R, and:
  * qualified names `BB10_champion_*.x` / `BB10_lead_*.x` become `Champion10.x` / `Lead10.x` (code only, not
    comments);
  * where two original files share one module, the second starts with `Transparent` for every constant the earlier
    ones made `Opaque`: Opaque is not carried over by Require/Import (checked), but it does persist inside one file.

  python gen_selfcontained_n1.py OUT.v --mini   writes the quick test: everything except BB10_n1.v's body after its
  first 160 lines and BB10_n1_bound.v, and no final section (catches merge errors in a few minutes).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROOFS = HERE.parent
ROOT = PROOFS.parents[1]
BUSY = ROOT / 'third_party' / 'busycoq' / 'verify'

# short names used in the sources -> full library paths (so that `Import` is unambiguous)
FULL = {
    'Bool': 'Coq.Bool.Bool', 'Bool.Sumbool': 'Coq.Bool.Sumbool',
    'Lists.List': 'Coq.Lists.List', 'List': 'Coq.Lists.List', 'Coq.Lists.List': 'Coq.Lists.List',
    'Lists.Streams': 'Coq.Lists.Streams',
    'Lia': 'Coq.micromega.Lia', 'Coq.micromega.Lia': 'Coq.micromega.Lia',
    'ZifyClasses': 'Coq.micromega.ZifyClasses',
    'PArith.BinPos': 'Coq.PArith.BinPos', 'PArith.Pnat': 'Coq.PArith.Pnat',
    'NArith.BinNat': 'Coq.NArith.BinNat', 'NArith.Nnat': 'Coq.NArith.Nnat',
    'ZArith': 'Coq.ZArith.ZArith', 'PeanoNat': 'Coq.Arith.PeanoNat',
    'Program.Tactics': 'Coq.Program.Tactics', 'Coq.Program.Equality': 'Coq.Program.Equality',
    'Logic.FunctionalExtensionality': 'Coq.Logic.FunctionalExtensionality',
    'Coq.Logic.ProofIrrelevance': 'Coq.Logic.ProofIrrelevance',
    'Coq.Arith.Compare_dec': 'Coq.Arith.Compare_dec',
    'Coq.Numbers.BinNums': 'Coq.Numbers.BinNums', 'Coq.ZArith.BinInt': 'Coq.ZArith.BinInt',
    'Wf_nat': 'Coq.Arith.Wf_nat',
}
# imported once at the top of the output (every one of our own files imports exactly these)
TOP_IMPORTS = {'Lia', 'PeanoNat', 'List'}

NAME = r'\w+(?:\.\w+)*'
REQ = re.compile(rf'(?:From[ \t]+(Coq|BusyCoq|BB8)[ \t]+)?\bRequire[ \t]+(?:(Import|Export)[ \t]+)?'
                 rf'({NAME}(?:[ \t]+{NAME})*)[ \t]*\.')
PRINT_ASSUMPTIONS = re.compile(r'^\s*Print Assumptions\s+[\w.]+\s*\.\s*$')

hoisted: set[str] = set()


def code_segments(text: str):
    """Yield (is_code, segment) with Coq comments (nested) separated from code."""
    i, depth, start = 0, 0, 0
    while i < len(text):
        if text.startswith('(*', i):
            if depth == 0 and i > start:
                yield True, text[start:i]
                start = i
            depth += 1
            i += 2
        elif text.startswith('*)', i) and depth > 0:
            depth -= 1
            i += 2
            if depth == 0:
                yield False, text[start:i]
                start = i
        else:
            i += 1
    if start < len(text):
        yield depth == 0, text[start:]


def rewrite_requires(text: str, ours: bool) -> str:
    """Hoist `Require` to the top; keep the import effect in place as `Import`/`Export` (code only, not comments)."""
    return ''.join(REQ.sub(lambda m: require_sub(m, ours), seg) if is_code else seg
                   for is_code, seg in code_segments(text))


def require_sub(m: re.Match, ours: bool) -> str:
    """`From Coq Require Import X` -> `Import <full X>` in place (X hoisted to the top); `From BusyCoq Require
    Export X` -> `Export BusyCoq_X` in place (so that notation precedence follows the original import order, e.g.
    Helper's sumbool `&&` after Bool's); `From BB8 Require ...` -> nothing (that content is inline, at top level)."""
    root, kind, names = m.group(1), m.group(2), m.group(3).split()
    if root == 'BB8':
        return ''
    if root == 'BusyCoq':
        return '' if kind is None else f'{kind} {" ".join(f"BusyCoq_{n}" for n in names)}.'
    full = []
    for n in names:
        if n not in FULL:
            raise SystemExit(f'unknown library {n!r} in {m.group(0)!r}')
        hoisted.add(FULL[n])
        full.append(FULL[n])
    return '' if kind is None else f'{kind} {" ".join(full)}.'



GROUP_RENAMES = [('BB10_champion_1RB1RA', 'Champion10'), ('BB10_champion_bound', 'Champion10'),
                 ('BB10_lead_1RB0RA', 'Lead10'), ('BB10_lead_bound', 'Lead10'), ('BB10_lead_vs_champion', 'Lead10')]
QUAL = re.compile(r'\b(' + '|'.join(o for o, _ in GROUP_RENAMES) + r')\.(?=[A-Za-z_])')
# `Opaque n1 n2 ... .` (names may be qualified: the sentence ends at a '.' followed by white space)
OPAQUE = re.compile(r'(?<![\w.])Opaque((?:\s+[\w\'.]*[\w\'])+)\s*\.(?=\s|$)')


def rename_qualified(text: str) -> str:
    """`BB10_champion_1RB1RA.tm` -> `Champion10.tm` etc., in code segments only."""
    m = dict(GROUP_RENAMES)
    return ''.join(QUAL.sub(lambda mm: m[mm.group(1)] + '.', seg) if is_code else seg
                   for is_code, seg in code_segments(text))


def opaque_names(text: str) -> list[str]:
    names = []
    for is_code, seg in code_segments(text):
        if is_code:
            for mm in OPAQUE.finditer(seg):
                names += mm.group(1).split()
    return names


STATE_H = '''(* Textual change (with the same one for busycoq's [dir] in TM above; besides these, only the renaming of
   qualified names described in the header).  The constructors of [state] are named St_A ... St_J here, with the
   abbreviations A ... J, so that A ... J are not global constants of THIS library: when Coq invents a name
   (anonymous `pose proof`, bare `intros` on `forall L t ts A, ...`) it skips the names of globals defined in the
   current library, and the original proofs, where the constructors came from another compiled file, rely on the
   invented names (H, H0, ...; the binder names A, L themselves).  A renamed constructor behind an abbreviation is
   not a global for that check; patterns, notations and printing are unaffected: `tm (H, 0)`, `| A, 0 => ...` and
   `{{H}}>` mean exactly what they meant. *)
Inductive state := St_A | St_B | St_C | St_D | St_E | St_F | St_G | St_H | St_I | St_J.
Notation A := St_A.  Notation B := St_B.  Notation C := St_C.  Notation D := St_D.  Notation E := St_E.
Notation F := St_F.  Notation G := St_G.  Notation H := St_H.  Notation I := St_I.  Notation J := St_J.'''

DIR_OLD = 'Inductive dir : Type := L | R.'
DIR_NEW = '''(* Textual change in this inlined file: the constructors are named St_L, St_R behind the abbreviations L, R, for
   the reason given at [state] below (the original proofs rely on `intros` naming a binder L or R as L or R). *)
Inductive dir : Type := St_L | St_R.
Notation L := St_L.
Notation R := St_R.'''

SYM_FIRST = ('(* Each original file started with the symbol scope on top (from Individual102\'s `Open Scope sym`);\n'
             '   restore that here, since the previous part may have ended in nat_scope. *)\n'
             'Local Open Scope sym_scope.\n\n')

MINI_CUT = 0   # > 0: keep only the first lines of BB10_n1.v (up to the first `Qed.` at or after this line)


def body(path: Path, ours: bool) -> str:
    text = path.read_text(encoding='utf-8')
    if MINI_CUT and path.name == 'BB10_n1.v':
        lines = text.splitlines()
        k = next(i for i in range(MINI_CUT, len(lines)) if lines[i].strip() == 'Qed.')
        text = '\n'.join(lines[:k + 1]) + '\n'
    text = rewrite_requires(text, ours)
    if ours:
        text = rename_qualified(text)
    lines = [l for l in text.splitlines() if not PRINT_ASSUMPTIONS.match(l)]
    text = '\n'.join(lines).rstrip() + '\n'
    return (SYM_FIRST + text) if ours else text


def bb102_body() -> str:
    """BB102.v with the constructors renamed St_A ... St_J behind the abbreviations A ... J (see STATE_H)."""
    text = body(PROOFS / 'BB102.v', ours=False)
    old = 'Inductive state := A | B | C | D | E | F | G | H | I | J.'
    assert text.count(old) == 1
    return text.replace(old, STATE_H)


def banner(title: str) -> str:
    return f'\n(* {"=" * 100} *)\n(* {title:^100} *)\n(* {"=" * 100} *)\n\n'


def busy_module(name: str) -> str:
    text = body(BUSY / f'{name}.v', ours=False)
    if name == 'TM':
        assert text.count(DIR_OLD) == 1
        text = text.replace(DIR_OLD, DIR_NEW)
    return (banner(f'busycoq/verify/{name}.v  (commit bd2e36f, MIT licence, see the header)') +
            f'Module BusyCoq_{name}.\n\n' + text +
            f'\nEnd BusyCoq_{name}.\nExport BusyCoq_{name}.\n')


def module(name: str, title: str, files: list[tuple[str, str]]) -> str:
    """Inline `files` (file name, banner title) inside `Module name`; reset Opaque between files."""
    out = [banner(f'Module {name}: {title}'), f'Module {name}.\n']
    opaque: list[str] = []
    for fname, ftitle in files:
        out.append(banner(f'bb8_list/proofs/{fname}: {ftitle}'))
        text = body(PROOFS / fname, ours=True)
        if opaque:
            out.append('(* The earlier file(s) of this module made these constants Opaque; in the multi-file build\n'
                       '   this file started with them transparent (Opaque is not carried over by Require). *)\n'
                       f'Transparent {" ".join(dict.fromkeys(opaque))}.\n\n')
        out.append(text)
        opaque += opaque_names(text)
    out.append(f'\nEnd {name}.\n')
    return ''.join(out)


HEADER = r'''(** * A Busy Beaver candidate for 10 states and 2 symbols that beats the BB(10) champion:
      a self-contained, machine-checked proof *)

(** Machine n1 (bbchallenge standard format; the undefined transition J0 is the halt):

      1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC

          0    1
      A  1RB  0RA
      B  1LC  1LF
      C  1RD  0LB
      D  1RA  1LE
      E  1LI  0LC
      F  0RG  1LD
      G  1RH  1LG
      H  1LC  0RG
      I  0LJ  0LI
      J  ---  0LC

    n1 is the G/H-swap sibling of the BB(8) record 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG with
    E0 := 1LI and two new states I = 0LJ0LI, J = ---0LC (bb8 project, Jeff Ketchersid with Claude, 2026-10-08).

    This file proves, with no axioms and no dependency other than the Coq standard library
    (arrow k a b = Knuth's a ^(k arrows) b, with arrow 0 a b = a * b; iter n g x = g^n (x)):

      n1_halts             : n1 halts from the blank tape.
      n1_score_exact       : the halting tape holds exactly 2 w + f + 3 k + 22 ones for some f, k and
                               w >= iter (2 JJ + 1) (fun n => arrow n 2 4) 34,   JJ = (3 T - 13) / 7,  T = arrow 37 2 3.
      n1_sigma_lower_bound : the number of ones exceeds  iter ((6 T - 19) / 7) (fun x => arrow (x + 1) 2 3) 33.
      n1_beats_M3_bound    : it exceeds  arrow (4T+41) 2 (arrow (4T+39) 2 (arrow (4T+35) 2 5))  (the proved lower bound
                             of another 10-state candidate, M3; not a comparison of exact scores).
      n1_beats_champion    : the BB(10) champion 1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ
                             (Racheline; Module Champion10: its own halting proof and exact score b2 + 3) halts with
                             Nc ones, n1 halts with No ones, and Nc + 1 < No + 1.
      n1_beats_lead        : the same against the 10-state candidate
                             1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC (Module Lead10).
      n1_fgh_level         : in the fast-growing hierarchy, f_(omega+1) ((3T - 13)/7 - 2) < N < f_(omega+1) (6T).
      n1_fgh_lower_64      : f_(omega+1) (64) < N.
      graham_lt_f_omega1_64: Graham's number < f_(omega+1) (64).
      n1_beats_graham      : Graham's number < N.

    Score convention.  busycoq stops BEFORE the undefined transition.  n1 and 0LJ0LC then read a 0 at the
    undefined J0, and the champion reads a 0 at E0 = 1RZ, so in each case the final 1RZ write adds one 1: the
    standard scores are No + 1, Nl + 1 and Nc + 1.  (With a final write of 0 the comparison is Nc < No, the same
    inequality.)

    How to check (Coq 8.20.1):

      coqc BB10_n1_selfcontained.v

    The last lines of the output must be "Closed under the global context", once for each of the twenty-eight
    `Print Assumptions` at the end of this file.  The only warnings are deprecation notices, LibTactics'
    `ltac_Mark` notice and notation re-declarations.

    Conventions.  Configurations, steps and halting are busycoq's (module TM below): a configuration is
    (state, (left stream, head symbol, right stream)); `halted tm c` means that the transition for the current
    (state, symbol) is undefined, and `halts tm c0` that such a configuration is reached from the blank tape
    `c0 = (A, (0^inf, 0, 0^inf))`.  `ones c N` says the tape of c is a finite list L, the head symbol s and a finite
    list R (then 0s) with N ones in L, s and R.

    Structure of this file.
      1. busycoq's core library (meithecatte/busycoq, verify/ directory, commit bd2e36f; MIT licence below),
         inlined verbatim, one module per file:  LibTactics, Helper, TM, Compute, Flip, Permute, Individual.
      2. The 10-state instantiation BB102 / Individual102 (as busycoq's BB52 / Individual52).
      3. Module Champion10: the BB(10) champion halts (digit-list counter, rules R1-R4) and its exact score
         (BB10_champion_1RB1RA.v, BB10_champion_bound.v).
      4. Module Lead10: 0LJ0LC halts, its exact score, and its score exceeds the champion's
         (BB10_lead_1RB0RA.v, BB10_lead_bound.v, BB10_lead_vs_champion.v).
      5. Module N1: n1 halts (BB10_n1.v: 6447 literal steps, then the B-form rules R1, R2 and the clearing CLR
         proved at machine level for all parameters, JJ periods of the PERIOD stage, ENDGAME, HALT) and its score
         and comparisons (BB10_n1_bound.v), the closed form of the score (BB10_n1_exact.v), and its level in the
         fast-growing hierarchy and Graham's number (BB10_n1_fgh.v).
      6. The main theorems.
    The published multi-file set compiles the same eleven files in the order BB102, Individual102, BB10_n1,
    BB10_lead_1RB0RA, BB10_lead_bound, BB10_champion_1RB1RA, BB10_champion_bound, BB10_lead_vs_champion,
    BB10_n1_bound, BB10_n1_exact, BB10_n1_fgh.  Here each machine's files stay together in one module, so the
    modules come in dependency order (Champion10 before Lead10, whose comparison file uses it, and both before N1,
    whose score file uses them); within each module the files keep that order.
    The original multi-file development is in bb8_list/proofs; this file was assembled from it by
    gen_selfcontained_n1.py without changing any proof text: `Require` lines are hoisted or turned into `Import`,
    each inlined file starts in the symbol scope as it originally did, the three developments are wrapped in
    modules and the qualified names BB10_champion_*.x, BB10_lead_*.x are renamed Champion10.x, Lead10.x (in code;
    the comments keep the original file names), and where two original files share a module the later one starts
    with `Transparent` for the constants the earlier one made Opaque (Opaque does not cross a Require).  The only
    other textual changes rename constructors behind abbreviations with their old names: in BB102 the states are
    St_A ... St_J with `Notation A := St_A` ... `Notation J := St_J`, and in busycoq's TM.v the directions are
    St_L, St_R with `Notation L := St_L`, `Notation R := St_R` (see the comment at [state]; this keeps the names
    Coq invents in proofs, e.g. for `intros` on `forall L t ts A, ...`, the same as in the multi-file build).

    busycoq licence (third_party/busycoq/LICENSE):
      Copyright (c) 2023 Maja Kadziolka.  Permission is hereby granted, free of charge, to any person obtaining a
      copy of this software and associated documentation files (the "Software"), to deal in the Software without
      restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute,
      sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do
      so, subject to the following conditions: The above copyright notice and this permission notice shall be
      included in all copies or substantial portions of the Software.  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT
      WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
      LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
      FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    LibTactics.v (MIT X11 licence, third_party/busycoq/LICENSE-LibTactics): Copyright (c) 2018 Arthur Chargueraud;
      same permission notice as above, and: except as contained in this notice, the name of the copyright holders
      shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software
      without prior written authorization from the copyright holders. *)

'''

FINAL = r'''
(* ==================================================================================================== *)
(** * Main results, stated with one [ones] predicate for the three machines *)

Set Default Goal Selector "!".
Local Open Scope nat_scope.

(** Knuth's up-arrow and iteration, exactly the definitions of module N1 (abbreviations, not copies):
      arrow 0 a b = a * b,   arrow (S k) a b = (arrow k a)^b (1)   (so arrow 1 2 x = 2^x, arrow k 2 3 = 2 ^(k arrows) 3);
      iter 0 g x = x,        iter (S n) g x = g (iter n g x). *)
Notation arrow := N1.arrow.
Notation iter := N1.iter.

(** [ones c N]: the tape of c is  Ls (reversed, left of the head), s (head cell), Rs (right of the head), with 0s
    beyond both lists, and N = the number of 1s in Ls, s and Rs. *)
Definition sym_val (s : Sym) : nat :=
  match s with
  | S0 => 0
  | S1 => 1
  end.

Fixpoint count1 (xs : list Sym) : nat :=
  match xs with
  | [] => 0
  | x :: t => sym_val x + count1 t
  end.

Definition ones (c : state * tape) (N : nat) : Prop :=
  exists (q : state) (Ls Rs : list Sym) (s : Sym),
    c = (q, (Ls *> const S0, s, Rs *> const S0)) /\ N = count1 Ls + sym_val s + count1 Rs.

(** The [ones] of the three developments (with their [count1], [sym_val]) are copies of it: convertible. *)
Lemma ones_N1 : forall c N, N1.ones c N <-> ones c N.
Proof. intros c N. split; intros Hc; exact Hc. Qed.

Lemma ones_Champion10 : forall c N, Champion10.ones c N <-> ones c N.
Proof. intros c N. split; intros Hc; exact Hc. Qed.

Lemma ones_Lead10 : forall c N, Lead10.ones c N <-> ones c N.
Proof. intros c N. split; intros Hc; exact Hc. Qed.

(** n1 halts from the blank tape. *)
Theorem n1_halts : halts N1.tm c0.
Proof. exact N1.halt. Qed.

(** The exact number of ones at the halt, with the bound on w in closed form
    (N1.JJ = (3 N1.T - 13) / 7, N1.T_def : N1.T = arrow 37 2 3, N1.F n = arrow n 2 4). *)
Theorem n1_score_exact : exists c f k w,
  c0 -[ N1.tm ]->* c /\ halted N1.tm c /\ ones c (2 * w + f + 3 * k + 22) /\
  iter (2 * ((3 * arrow 37 2 3 - 13) / 7) + 1) (fun n => arrow n 2 4) 34 <= w.
Proof.
  destruct N1.score_exact as (c & f & k & w & H1 & H2 & H3 & H4).
  unfold N1.JJ in H4. rewrite N1.T_def in H4.
  replace N1.F with (fun n => arrow n 2 4) in H4 by reflexivity.
  exists c, f, k, w.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_N1 _ _) H3) | exact H4]]].
Qed.

(** The verifier's lower bound G^((6T-19)/7) (33), with G x = 2 ^(x+1 arrows) 3 and T = 2 ^(37 arrows) 3. *)
Theorem n1_sigma_lower_bound : exists c N,
  c0 -[ N1.tm ]->* c /\ halted N1.tm c /\ ones c N /\
  iter ((6 * arrow 37 2 3 - 19) / 7) (fun x => arrow (x + 1) 2 3) 33 < N.
Proof.
  destruct N1.sigma_lower_bound as (c & N & H1 & H2 & H3 & H4).
  exists c, N.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_N1 _ _) H3) | exact H4]]].
Qed.

(** n1 exceeds the proved lower bound of the 10-state candidate M3 (a lower bound only, not M3's score). *)
Theorem n1_beats_M3_bound : exists c N,
  c0 -[ N1.tm ]->* c /\ halted N1.tm c /\ ones c N /\
  arrow (4 * arrow 37 2 3 + 41) 2 (arrow (4 * arrow 37 2 3 + 39) 2 (arrow (4 * arrow 37 2 3 + 35) 2 5)) < N.
Proof.
  destruct N1.beats_M3_bound as (c & N & H1 & H2 & H3 & H4).
  exists c, N.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_N1 _ _) H3) | exact H4]]].
Qed.

(** The BB(10) champion halts with Nc ones (score Nc + 1: E0 = 1RZ writes a 1 on a 0); n1 halts with No ones
    (score No + 1: the undefined J0 is read on a 0); Nc + 1 < No + 1.  Champion10.score_exact gives Nc exactly. *)
Theorem n1_beats_champion : exists cc Nc co No,
  c0 -[ Champion10.tm ]->* cc /\ halted Champion10.tm cc /\ ones cc Nc /\
  c0 -[ N1.tm ]->* co /\ halted N1.tm co /\ ones co No /\
  Nc + 1 < No + 1.
Proof.
  destruct N1.beats_champion as (cc & Nc & co & No & H1 & H2 & H3 & H4 & H5 & H6 & H7).
  exists cc, Nc, co, No.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_Champion10 _ _) H3) |]]].
  split; [exact H4 | split; [exact H5 | split; [exact (proj1 (ones_N1 _ _) H6) | exact H7]]].
Qed.

(** The same against the 10-state candidate 0LJ0LC (score Nl + 1: the undefined J0 is read on a 0). *)
Theorem n1_beats_lead : exists cl Nl co No,
  c0 -[ Lead10.tm ]->* cl /\ halted Lead10.tm cl /\ ones cl Nl /\
  c0 -[ N1.tm ]->* co /\ halted N1.tm co /\ ones co No /\
  Nl + 1 < No + 1.
Proof.
  destruct N1.beats_lead as (cl & Nl & co & No & H1 & H2 & H3 & H4 & H5 & H6 & H7).
  exists cl, Nl, co, No.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_Lead10 _ _) H3) |]]].
  split; [exact H4 | split; [exact H5 | split; [exact (proj1 (ones_N1 _ _) H6) | exact H7]]].
Qed.

(** The fast-growing hierarchy and Graham's number, exactly the definitions of module N1 (BB10_n1_fgh.v):
      fgh 0 n = n + 1,  fgh (k+1) n = (fgh k)^n (n),  f_omega n = fgh n n,  f_omega1 n = f_omega^n (n);
      up3 0 n = 3 * n,  up3 (k+1) n = (up3 k)^n (1)   (up3 k n = 3 ^(k arrows) n),
      graham_g 0 = 4,  graham_g (k+1) = up3 (graham_g k) 3,  Graham = graham_g 64. *)
Notation f_omega1 := N1.f_omega1.
Notation Graham := N1.Graham.

(** n1 sits at level omega+1 of the fast-growing hierarchy:
    f_(omega+1) ((3T - 13)/7 - 2) < N < f_(omega+1) (6T),  T = 2 ^(37 arrows) 3, for the exact count N. *)
Theorem n1_fgh_level : exists c N,
  c0 -[ N1.tm ]->* c /\ halted N1.tm c /\ ones c N /\
  f_omega1 ((3 * arrow 37 2 3 - 13) / 7 - 2) < N /\ N < f_omega1 (6 * arrow 37 2 3).
Proof.
  destruct N1.fgh_level as (c & N & H1 & H2 & H3 & H4).
  exists c, N.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_N1 _ _) H3) | exact H4]]].
Qed.

Theorem n1_fgh_lower_64 : exists c N,
  c0 -[ N1.tm ]->* c /\ halted N1.tm c /\ ones c N /\ f_omega1 64 < N.
Proof.
  destruct N1.fgh_lower_64 as (c & N & H1 & H2 & H3 & H4).
  exists c, N.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_N1 _ _) H3) | exact H4]]].
Qed.

Theorem graham_lt_f_omega1_64 : Graham < f_omega1 64.
Proof. exact N1.graham_lt_f_omega1_64. Qed.

(** n1 leaves more than Graham's number of ones. *)
Theorem n1_beats_graham : exists c N,
  c0 -[ N1.tm ]->* c /\ halted N1.tm c /\ ones c N /\ Graham < N.
Proof.
  destruct N1.beats_graham as (c & N & H1 & H2 & H3 & H4).
  exists c, N.
  split; [exact H1 | split; [exact H2 | split; [exact (proj1 (ones_N1 _ _) H3) | exact H4]]].
Qed.

(** ** No axioms *)
Print Assumptions Champion10.halt.
Print Assumptions Champion10.score_exact.
Print Assumptions Lead10.halt.
Print Assumptions Lead10.score_exact.
Print Assumptions Lead10.candidate_beats_champion.
Print Assumptions N1.halt.
Print Assumptions N1.score_exact.
Print Assumptions N1.sigma_lower_bound.
Print Assumptions N1.dominates.
Print Assumptions N1.beats_M3_bound.
Print Assumptions N1.beats_lead.
Print Assumptions N1.beats_champion.
Print Assumptions N1.score_closed_unfolded.
Print Assumptions N1.score_value_gt.
Print Assumptions N1.fgh_level.
Print Assumptions N1.fgh_lower_64.
Print Assumptions N1.graham_lt_f_omega1_64.
Print Assumptions N1.beats_graham.
Print Assumptions n1_halts.
Print Assumptions n1_score_exact.
Print Assumptions n1_sigma_lower_bound.
Print Assumptions n1_beats_M3_bound.
Print Assumptions n1_beats_champion.
Print Assumptions n1_beats_lead.
Print Assumptions n1_fgh_level.
Print Assumptions n1_fgh_lower_64.
Print Assumptions graham_lt_f_omega1_64.
Print Assumptions n1_beats_graham.
'''

PARTS_CHAMPION = [('BB10_champion_1RB1RA.v', 'the BB(10) champion halts'),
                  ('BB10_champion_bound.v', 'its exact score')]
PARTS_LEAD = [('BB10_lead_1RB0RA.v', 'the candidate 0LJ0LC halts'),
              ('BB10_lead_bound.v', 'its exact score'),
              ('BB10_lead_vs_champion.v', 'its score exceeds the champion\'s')]
PARTS_N1 = [('BB10_n1.v', 'n1 halts'),
            ('BB10_n1_bound.v', 'n1\'s score; it beats 0LJ0LC and the champion'),
            ('BB10_n1_exact.v', 'n1\'s score in closed form'),
            ('BB10_n1_fgh.v', 'n1 in the fast-growing hierarchy; Graham\'s number')]


def main() -> None:
    global MINI_CUT
    args = [a for a in sys.argv[1:] if a != '--mini']
    mini = '--mini' in sys.argv[1:]
    out = Path(args[0]) if args else HERE / 'BB10_n1_selfcontained.v'
    if mini:
        MINI_CUT = 160

    parts = []
    for name in ['LibTactics', 'Helper', 'TM', 'Compute', 'Flip', 'Permute', 'Individual']:
        parts.append(busy_module(name))
        if name == 'LibTactics':
            parts.append('(* LibTactics.v sets Implicit Arguments for its own definitions only. *)\n'
                         'Unset Implicit Arguments.\n')
    parts.append(banner('bb8_list/proofs/BB102.v and Individual102.v: busycoq instantiated to 10 states, 2 symbols'))
    parts.append(bb102_body())
    parts.append('\n' + body(PROOFS / 'Individual102.v', ours=False))

    parts.append(module('Champion10', 'the BB(10) champion (Racheline)', PARTS_CHAMPION))
    parts.append(module('Lead10', 'the 10-state candidate 0LJ0LC', PARTS_LEAD))
    parts.append(module('N1', 'the candidate n1', PARTS_N1[:1] if mini else PARTS_N1))
    if not mini:
        parts.append(FINAL)

    top = (HEADER +
           'From Coq Require Import Lia PeanoNat List.\nImport ListNotations.\n' +
           '(* every library used by the inlined files; each is imported where the original file imported it *)\n' +
           'Require ' + ' '.join(sorted(hoisted - {FULL[n] for n in TOP_IMPORTS})) + '.\n' +
           '(* no global `Set Default Goal Selector "!"` here: LibTactics.v is written without it; every later part\n'
           '   sets it for itself, as the original files do *)\n')
    text = top + ''.join(parts)
    out.write_text(text, encoding='utf-8', newline='\n')
    n_lines = text.count('\n')
    print(f'wrote {out} ({len(text.encode()) / 1e6:.2f} MB, {n_lines} lines)')
    # sanity: no Require left (outside comments) except the two hoisted lines at the top
    code = ''.join(seg for is_code, seg in code_segments(text) if is_code)
    leftover = [l for l in code.splitlines() if re.search(r'\bRequire\b', l)]
    if len(leftover) != 2:
        print('WARNING: unexpected Require sentences:', *leftover, sep='\n  ')
    stale = sorted(set(re.findall(r'\bBB10_\w+\.\w+', code)))
    if stale:
        print('WARNING: qualified names left in code:', stale)
    for l in code.splitlines():
        if l.lstrip().startswith('Transparent '):
            print('  reset:', l.strip())


if __name__ == '__main__':
    main()
