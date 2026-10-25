"""Family C7: the BB(7) champion 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF, exhaustion K(0^11; 0; b) in
follow2's default template (canonical state B, K word 11 D1^12 D(3b+2) D0 1001, SUF = '11001', E = 2).
import c7fam  registers the family in mf35g.FAMILIES."""
import sys
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import mf35g
mf35g.FAMILIES['C7'] = dict(base='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF', Q='B', SUF='11001', E=2,
                            word=lambda b: '11' + '101' * 12 + '10' * (3 * b + 2) + '1' + '11001')
