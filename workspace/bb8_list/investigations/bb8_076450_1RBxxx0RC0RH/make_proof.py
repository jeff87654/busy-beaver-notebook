"""Write the busycoq non-halting proof for
    1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH
by relabeling the proved variant BB8_76450_1RB1RA_G0_1LH_H0_1RB.v
(1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LH1LF_1RB---) with states A <-> H swapped.

The two machines are the same up to that swap, except for the start state: this machine starts in A, which
corresponds to the variant's H. Both of the corresponding 0-transitions (the variant's A0 and H0) are 1RB, so
the runs from the blank tape are identical after the first step. In the proof, state A appears only in the
tape notation `{{A}}` (the transfer phases TR1/TR2/ENTRY, TRF and the crossing lemma cr_AR_1_1). State H
appears only in the `tm` table. So the relabeling is: new tm table, `{{A}}` -> `{{H}}`, cr_AR_1_1 -> cr_HR_1_1,
and comment updates. The 50 literal steps in init_reach are re-executed by Coq against the new table.

Usage: python make_proof.py [out.v]   (default ../../proofs/BB8_76450_1RBxxx_0RC0RH.v)
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent.parent / 'proofs' / 'BB8_76450_1RB1RA_G0_1LH_H0_1RB.v'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent.parent / 'proofs' / 'BB8_76450_1RBxxx_0RC0RH.v'
M = '1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH'
V = '1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LH1LF_1RB---'

TABLE = """Definition tm : TM := fun '(q, s) =>
  match q, s with
  | A, 0 => Some (1, R, B)  | A, 1 => None
  | B, 0 => Some (0, R, C)  | B, 1 => Some (0, R, H)
  | C, 0 => Some (0, L, D)  | C, 1 => Some (1, R, C)
  | D, 0 => Some (1, R, E)  | D, 1 => Some (1, L, E)
  | E, 0 => Some (1, L, F)  | E, 1 => Some (0, L, G)
  | F, 0 => Some (1, L, B)  | F, 1 => Some (0, R, D)
  | G, 0 => Some (1, L, A)  | G, 1 => Some (1, L, F)
  | H, 0 => Some (1, R, B)  | H, 1 => Some (1, R, H)
  end."""

HEADER = """(** * BB(8) holdout, subtask 76450: %s never halts *)

(** This machine is the proved variant [BB8_76450_1RB1RA_G0_1LH_H0_1RB.v]
      %s
    with the state names A and H swapped; that variant is in turn a G0/H0 variant of [BB8_76450_1RB1RA.v].
    The start state differs: this machine starts in A (the variant's H), and the variant starts in A (this
    machine's H). Both of these states have the 0-transition 1RB, so after one step the two runs from the
    blank tape coincide. This file is the variant's proof with {{A}} replaced by {{H}} and a new [tm] table,
    written by bb8_list/investigations/bb8_076450_1RBxxx0RC0RH/make_proof.py.
    See bb8_list/investigations/bb8_076450_1RBxxx0RC0RH.md and bb8_076450_1RB1RA0RC0RA.md. *)

""" % (M, V)


def main():
    src = SRC.read_text(encoding='utf-8')
    # 1. replace the title line and the pointer to the investigation with the new header
    first, rest = src.split('\n', 1)
    assert first.startswith('(** * BB(8) holdout') and V in first
    rest = rest.lstrip('\n')
    assert rest.startswith('(** Formalization of [bb8_list/investigations/bb8_076450_1RB1RA0RC0RA.md].')
    rest = rest.replace('(** Formalization of [bb8_list/investigations/bb8_076450_1RB1RA0RC0RA.md].\n\n    ',
                        '(** ', 1)
    text = rest
    # 2. the machine string and the table
    assert text.count('(* machine: %s *)' % V) == 1
    text = text.replace('(* machine: %s *)' % V, '(* machine: %s *)' % M)
    text, n = re.subn(r"Definition tm : TM := fun '\(q, s\) =>.*?end\.", lambda _: TABLE, text, count=1, flags=re.S)
    assert n == 1
    # 3. state A -> H in tape notation and the crossing-lemma name; phase comments "A>" -> "H>"
    assert '{{H}}' not in text and 'cr_HR' not in text
    text = text.replace('{{A}}', '{{H}}').replace('cr_AR_1_1', 'cr_HR_1_1')
    text = re.sub(r'\bA>', 'H>', text)
    text = text.replace('Only END4b uses the transitions G0 and H0.',
                        'Only END4b uses the transitions G0 and A0 (besides the first step).')
    assert not re.search(r'\{\{A\}\}|\bA>', text)
    text = HEADER + text
    OUT.write_text(text, encoding='utf-8', newline='\n')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
