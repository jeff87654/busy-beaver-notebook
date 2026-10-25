"""Assemble ONE self-contained Coq file for the BB(9) record machine
   1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---

  python gen_selfcontained.py [OUT.v]        (default: BB9_record_1RB0RA_selfcontained.v next to this script)

The output depends only on the Coq standard library (tested with Coq 8.20.1):
  * busycoq's core (LibTactics, Helper, TM, Compute, Flip, Permute, Individual; commit bd2e36f, MIT) is inlined
    verbatim, each file wrapped in a module `BusyCoq_<File>` that is then `Export`ed, so that every file-local
    `Import` keeps its original scope;
  * BB92.v / Individual92.v (the 9-state instantiation) follow;
  * then, at top level, BB9_record_1RB0RA.v (halting) and BB9_record_bound.v (exact score);
  * Jacobzheng's champion (BB9_champion_1RB1RA.v, BB9_champion_bound.v) inside `Module Champion9`;
  * BB9_record_vs_champion.v (with `BB9_champion_*.` renamed to `Champion9.`);
  * a short final section stating the main results with a single `ones` predicate.
Only `Require` lines are rewritten (hoisted to the top, or turned into `Import`); `Print Assumptions` lines are
collected at the end.  Everything else is copied byte for byte.
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


STATE_H = '''(* The only textual change to any inlined file.  The constructor for state H is named St_H here, with the
   abbreviation H, so that `H` is not a global constant of THIS library: when Coq invents a hypothesis name
   (anonymous `pose proof`, bare `intros`) it skips the names of globals defined in the current library, and the
   original proofs, where H came from another compiled file, rely on the invented names H, H0, ... (a renamed
   constructor behind an abbreviation is not a global for that check; patterns, notations and printing are
   unaffected: `tm (H, 0)` and `{{H}}>` mean exactly what they meant). *)
Inductive state := A | B | C | D | E | F | G | St_H | I.
Notation H := St_H.'''

SYM_FIRST = ('(* Each original file started with the symbol scope on top (from Individual92\'s `Open Scope sym`);\n'
             '   restore that here, since the previous part may have ended in nat_scope. *)\n'
             'Local Open Scope sym_scope.\n\n')


def body(path: Path, ours: bool) -> str:
    text = path.read_text(encoding='utf-8')
    text = rewrite_requires(text, ours)
    lines = [l for l in text.splitlines() if not PRINT_ASSUMPTIONS.match(l)]
    text = '\n'.join(lines).rstrip() + '\n'
    return (SYM_FIRST + text) if ours else text


def bb92_body() -> str:
    """BB92.v with the constructor H renamed St_H behind the abbreviation H (see STATE_H)."""
    text = body(PROOFS / 'BB92.v', ours=False)
    old = 'Inductive state := A | B | C | D | E | F | G | H | I.'
    assert text.count(old) == 1
    return text.replace(old, STATE_H)


def banner(title: str) -> str:
    return f'\n(* {"=" * 100} *)\n(* {title:^100} *)\n(* {"=" * 100} *)\n\n'


def busy_module(name: str) -> str:
    return (banner(f'busycoq/verify/{name}.v  (commit bd2e36f, MIT licence, see the header)') +
            f'Module BusyCoq_{name}.\n\n' + body(BUSY / f'{name}.v', ours=False) +
            f'\nEnd BusyCoq_{name}.\nExport BusyCoq_{name}.\n')


HEADER = r'''(** * A new Busy Beaver champion for 9 states and 2 symbols: a self-contained, machine-checked proof *)

(** Machine (bbchallenge standard format; the undefined transition I1 is the halt):

      1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---

          0    1
      A  1RB  0RA
      B  1LC  1LF
      C  1RD  0LB
      D  1RA  1LE
      E  1LI  0LC
      F  1RG  1LD
      G  0RH  0RF
      H  0RG  0RE
      I  0LH  ---

    Found 2026-10-06 (Jeff Ketchersid, with Claude) in a 9-state extension of the BB(7)-champion prefix.  Its
    first 8 states and 15 defined transitions are those of the BB(7) champion; E0 leads to the new state I.

    This file proves, with no axioms and no dependency other than the Coq standard library:

      halt                : the machine halts from the blank tape.
      score_closed        : the halting tape holds exactly
                               3 * (2 ^(12 Bx - 9 arrows) 8) + 108 * (Bx / 5) + 70   ones,  with  2 Bx + 4 = 2 ^13 3,
                            i.e. with T = 2 ^(13 arrows) 3:   sigma = 3 * (2 ^(6T - 33 arrows) 8) + (54 T + 26) / 5.
      sigma_lower_bound   : the number of ones exceeds 2 ^(2 ^13 3 arrows) 3   (Knuth up-arrows, base 2).
      Champion9.halt, Champion9.score_exact :
                            Jacobzheng's 2024 champion 1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH
                            halts with exactly Champion9.b2 + 3 ones on the tape (plus the 1 written by 1RZ).
      new_champion        : both machines halt, the champion with Nc ones and ours with No ones, and Nc + 1 < No.
      new_champion_margin : the same with 3 * (Nc + 1) < No, so the convention for the symbol written by the final
                            transition (ours reads a 1 at the halt, the champion a 0) cannot affect the comparison.

    How to check (Coq 8.20.1; about 45 minutes, almost all of it the machine-level lemmas of the halting proof):

      coqc BB9_record_1RB0RA_selfcontained.v

    The last lines of the output must be twelve times "Closed under the global context" (the `Print Assumptions`
    of the twelve main theorems at the end of this file).  The only warnings are deprecation notices.

    Conventions.  Configurations, steps and halting are busycoq's (module TM below): a configuration is
    (state, (left stream, head symbol, right stream)); `halted tm c` means that the transition for the current
    (state, symbol) is undefined, and `halts tm c0` that such a configuration is reached from the blank tape
    `c0 = (A, (0^inf, 0, 0^inf))`.  `ones c N` says the tape of c is a finite list L, the head symbol s and a finite
    list R (then 0s) with N ones in L, s and R.  `arrow k a b` is Knuth's a ^(k arrows) b, with arrow 0 a b = a * b.
    The score of a halting machine is the number of ones after the halting transition is applied: the undefined
    transition I1 is reached with the head on a 1, so writing 1 (the 1RZ convention) leaves the count at No;
    the champion's E0 = 1RZ writes a 1 on a 0, so its score is Nc + 1.  new_champion_margin covers every other
    convention.

    Structure of this file.
      1. busycoq's core library (meithecatte/busycoq, verify/ directory, commit bd2e36f; MIT licence below),
         inlined verbatim, one module per file:  LibTactics, Helper, TM, Compute, Flip, Permute, Individual.
      2. The 9-state instantiation BB92 / Individual92 (as busycoq's BB52 / Individual52).
      3. The halting proof: 2149 literal steps to the BB(7) champion's digit-list family; the champion rules R1-R3
         proved at machine level for all parameters (generated lemmas); the exact clearing of the list down to
         K(0^11; 0; Bx) with Bx = U 10 (U 10 0) (2 Bx + 4 = 2 ^13 3); the REBUILD of a 12Bx-11 digit list with the
         tail tokens [20; 4; 21; 4]; the clearing of the token 20 to 2 (CLR2); the D2 stage, which halts because
         12 Bx - 11 = 1 (mod 5) (lemma Bx_mod5, from arrow k 2 n = 1 (mod 5) for k >= 2, n >= 3).
      4. The exact score and closed forms (BB9_record_bound.v).
      5. Module Champion9: the 2024 champion halts (digit-list counter with parity-controlled restart) and its
         exact score b2 + 3 (BB9_champion_1RB1RA.v, BB9_champion_bound.v).
      6. The comparison (BB9_record_vs_champion.v): b2 < 2 ^(b1+4 arrows) (b1+6) with b1 <= 2 ^(10 arrows) 11, far
         below our 2 ^(12Bx-9 arrows) 8.
      7. The main theorems.
    The original multi-file development is in github.com/jeff87654/busy-beaver (BB9/); this file was assembled from
    it by gen_selfcontained.py without changing any proof text: `Require` lines are hoisted or turned into `Import`,
    each inlined file starts in the symbol scope as it originally did, the champion's files are wrapped in a module
    and its qualified names renamed.  The one textual change is in BB92: the constructor of state H is named St_H
    behind the abbreviation `Notation H := St_H` (see the comment there; it keeps Coq's invented hypothesis names
    H, H0, ... the same as in the multi-file build).

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
(** * Main results, stated with one [ones] predicate for both machines *)

Set Default Goal Selector "!".
Local Open Scope nat_scope.

(** [Champion9.ones] and [ones] are the same count: the two definitions (and their [count1], [sym_val]) are
    copies, so the two predicates are convertible. *)
Lemma count1_agree : forall xs, Champion9.count1 xs = count1 xs.
Proof. intros xs. induction xs as [| x xs IH]; [reflexivity |]. simpl. rewrite IH. destruct x; reflexivity. Qed.

Lemma ones_agree : forall c N, Champion9.ones c N <-> ones c N.
Proof. intros c N. split; intros H; exact H. Qed.

(** The margin, with the same arithmetic as [record_beats_champion]: three times the champion's standard score
    b2 + 4 is still below our count of ones 6 bp + 108 (Bx/5) + 82 (indeed 2 bp + 4 >= b2 + 5). *)
Lemma margin_core : 3 * (Champion9.b2 + 4) < 6 * bp + 108 * (Bx / 5) + 82.
Proof.
  pose proof b2_le as Eb2. pose proof b1_le as Eb1. pose proof bp_closed as Ebp.
  pose proof Bx_arrow13 as E13. pose proof Bx_ge6 as H6.
  pose proof A13_ge as F1. pose proof A11_7 as F2.
  pose proof (A_lin 10 11 ltac:(lia) ltac:(lia)) as F3.
  pose proof (A_lin 10 12 ltac:(lia) ltac:(lia)) as F3'.
  assert (HK : Champion9.b1 + 5 <= 12 * Bx - 9).
  { assert (E : arrow 10 2 12 = arrow 9 2 (arrow 10 2 11)) by (rewrite (arrow_SS 9 2 11); reflexivity).
    pose proof (A_lin 9 (arrow 10 2 11) ltac:(lia) ltac:(pose proof (A_id 10 11); lia)) as F4.
    lia. }
  assert (H7 : Champion9.b1 + 7 <= arrow (12 * Bx - 9) 2 7).
  { pose proof (arrow_level_mono (12 * Bx - 9 - 11) 11 7) as L.
    replace (12 * Bx - 9 - 11 + 11) with (12 * Bx - 9) in L by lia.
    assert (E : arrow 10 2 12 = arrow 9 2 (arrow 10 2 11)) by (rewrite (arrow_SS 9 2 11); reflexivity).
    pose proof (A_lin 9 (arrow 10 2 11) ltac:(lia) ltac:(pose proof (A_id 10 11); lia)) as F4.
    lia. }
  pose proof (compare_core Champion9.b1 (12 * Bx - 9) HK H7) as Hc.
  generalize dependent (Bx / 5). intros. lia.
Qed.

(** The champion halts with Nc ones on its tape (standard score Nc + 1, E0 = 1RZ writes a 1 on a 0); our machine
    halts with No ones (standard score No, the head reads a 1 at the undefined I1); and Nc + 1 < No. *)
Theorem new_champion :
  exists cc Nc co No,
    c0 -[ Champion9.tm ]->* cc /\ halted Champion9.tm cc /\ ones cc Nc /\
    c0 -->* co /\ halted tm co /\ ones co No /\
    Nc + 1 < No.
Proof.
  destruct sigma_ours_gt_champion as (cc & Nc & co & No & H1 & H2 & H3 & H4 & H5 & H6 & H7).
  pose proof (proj1 (ones_agree cc Nc) H3) as H3'.
  exists cc, Nc, co, No. repeat split; assumption.
Qed.

(** Whatever symbol the final transition is taken to write, on either machine, ours has more ones. *)
Corollary new_champion_margin :
  exists cc Nc co No,
    c0 -[ Champion9.tm ]->* cc /\ halted Champion9.tm cc /\ ones cc Nc /\
    c0 -->* co /\ halted tm co /\ ones co No /\
    3 * (Nc + 1) < No.
Proof.
  destruct Champion9.score_exact as (cc & Hc1 & Hc2 & Hc3).
  destruct score_exact as (co & Ho1 & Ho2 & Ho3).
  pose proof (proj1 (ones_agree _ _) Hc3) as Hc3'.
  exists cc, (Champion9.b2 + 3), co, (6 * bp + 108 * (Bx / 5) + 82).
  repeat split; try assumption.
  pose proof margin_core as Hm. revert Hm. generalize (Bx / 5). generalize Champion9.b2. generalize bp.
  intros p b m Hm. lia.
Qed.

(** ** No axioms *)
Print Assumptions halt.
Print Assumptions score_exact.
Print Assumptions score_closed.
Print Assumptions Bx_arrow13.
Print Assumptions sigma_lower_bound.
Print Assumptions sigma_lower_bound_strong.
Print Assumptions Champion9.halt.
Print Assumptions Champion9.score_exact.
Print Assumptions record_beats_champion.
Print Assumptions sigma_ours_gt_champion.
Print Assumptions new_champion.
Print Assumptions new_champion_margin.
'''


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'BB9_record_1RB0RA_selfcontained.v'

    parts = []
    for name in ['LibTactics', 'Helper', 'TM', 'Compute', 'Flip', 'Permute', 'Individual']:
        parts.append(busy_module(name))
        if name == 'LibTactics':
            parts.append('(* LibTactics.v sets Implicit Arguments for its own definitions only. *)\n'
                         'Unset Implicit Arguments.\n')
    parts.append(banner('bb8_list/proofs/BB92.v and Individual92.v: busycoq instantiated to 9 states, 2 symbols'))
    parts.append(bb92_body())
    parts.append('\n' + body(PROOFS / 'Individual92.v', ours=False))

    parts.append(banner('bb8_list/proofs/BB9_record_1RB0RA.v: the machine halts'))
    parts.append(body(PROOFS / 'BB9_record_1RB0RA.v', ours=True))
    parts.append(banner('bb8_list/proofs/BB9_record_bound.v: the exact score and lower bounds'))
    parts.append(body(PROOFS / 'BB9_record_bound.v', ours=True))

    parts.append(banner('Module Champion9: the 2024 champion halts (BB9_champion_1RB1RA.v), exact score (BB9_champion_bound.v)'))
    parts.append('Module Champion9.\n\n')
    parts.append(body(PROOFS / 'BB9_champion_1RB1RA.v', ours=True))
    parts.append('\n' + body(PROOFS / 'BB9_champion_bound.v', ours=True))
    parts.append('\nEnd Champion9.\n')

    parts.append(banner('bb8_list/proofs/BB9_record_vs_champion.v: our exact score beats the champion\'s exact score'))
    vs = body(PROOFS / 'BB9_record_vs_champion.v', ours=True)
    vs = vs.replace('BB9_champion_bound.', 'Champion9.').replace('BB9_champion_1RB1RA.', 'Champion9.')
    parts.append(vs)

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


if __name__ == '__main__':
    main()
