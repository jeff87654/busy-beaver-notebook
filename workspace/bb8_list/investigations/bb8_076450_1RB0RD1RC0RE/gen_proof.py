"""Write the busycoq non-halting proofs from proof_template.v.in.
  python gen_proof.py main    ..\\..\\proofs\\BB8_76450_1RB0RD.v
  python gen_proof.py h0_1lc  ..\\..\\proofs\\BB8_76450_1RB0RD_H0_1LC.v
"""
import sys

V = {
    'main': ('1RB0RD_1RC0RE_1LD1LC_1LA0LD_1LB1RF_---1LG_0RB1RH_0LB1RG', 'Some (0, L, B)', ''),
    'h0_1lc': ('1RB0RD_1RC0RE_1LD1LC_1LA0LD_1LB1RF_---1LG_0RB1RH_1LC1RG', 'Some (1, L, C)',
               ' (H0 variant: H0 1LC gives the same tape as the main machine\'s detour\n'
               '    H0 0LB, B1 0RE, E0 1LB, B0 1RC, C1 1LC, 4 steps sooner; H0 is read only at the turn of rule O,\n'
               '    so every lemma and proof script is the same as for the main machine)'),
}
m, h0, note = V[sys.argv[1]]
s = open('proof_template.v.in', encoding='utf-8').read()
s = s.replace('@MACHINE@', m).replace('@H0@', h0).replace('@VARIANT@', note)
open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(s)
print('wrote', sys.argv[2])
