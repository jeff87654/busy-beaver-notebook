import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from backtrack_c4_9state import parse_tm, make_exhaustion_tape, check_valid_odd_k, run_fixed_tm, format_tape

# Let's check what happens to the 9-state extensions of C1=1RH H0=0RB H1=0LD!
# In 8 states: C1=1RH, H0=0RB, H1=0LD.
# How can we extend this to 9 states (+I) so that 1 slot of (H, I) is unused on k=3, 21
# OR is hit on k=4, 6?!
# Wait: on k=3, 21, C1=1RH H0=0RB H1=0LD uses ALL 3 SLOTS (C1, H0, H1)!
# Because it uses all 3 slots (C1, H0, H1) on k=3, 21:
# If we want a 9-state extension that behaves like C1=1RH H0=0RB H1=0LD on k=3, 21,
# ONE of C1, H0, or H1 MUST jump to state I (8)!
# And then from state I, one slot (I0 or I1) must continue the transition, while the OTHER slot of I is --- (HALT)!
# WAIT A SECOND!
# If C1 jumps to H (1 step), and H jumps to I (1 step), and I jumps to B or D (1 step),
# that is THREE steps instead of TWO steps (C -> H -> B/D)!
# Why did C -> H -> B/D take 2 steps in 8 states, whereas C -> H -> I -> B/D takes 3 steps?!
# WAIT A MINUTE!
# In 9 states, why did we force C1 to jump ONLY to H (`c1_moves = [(w, d, 7) ...]`) when
# H0 could jump to B and H1 could jump to I, OR C1 could jump to H (on 1), H0 to B, and H1 to I?!
# Wait: if C1=1RH, H0=0RB, and H1 jumps to I (say H1=0LI or 0RI or 1LI or 1RI),
# then whenever H1 was reached in the 8-state machine (which was `10011 H[1] 0011...`),
# in the 8-state machine `H1 = 0LD` wrote 0 and moved LEFT to `1001 D[1] 00011...`!
# If instead `H1 = 0LI`, it writes 0 and moves LEFT to `1001 I[1] 00011...`!
# Then `I[1]` is on `1` (the `1` of `1001`), NOT on `D[1]`!
# Whereas in the 8-state machine, `1001 D[1] 00011...` executed `D1 = 0LD`, writing 0 and moving LEFT to `100 D[0] 00011...`!
# SO IF `H1 = 0LI` AND `I1 = 0LD`, THEN `H1 -> I1 -> D` EXECUTES THE EXACT SAME TWO STEPS AS `H1 = 0LD -> D1 = 0LD`!!

# HOLD EVERYTHING!!
# READ THAT AGAIN!!
# In the base machine C4_1 / C4_2:
#   D0 = 0LE,  D1 = 0LD !
#   E0 = 0LF,  E1 = 1LE !
#   F0 = 1RA,  F1 = 1LF !
#   B0 = 1RC,  B1 = 1RB !
# Every time a gadget transitions to D, E, F, or B (say `H1 = 0LD`), on the VERY NEXT STEP the base machine executes `D0` or `D1`!
# Therefore, if we replace `H1 = 0LD` with `H1 = 0LI`, and we set:
#   I1 = D1 = 0LD (or I0 = D0 = 0LE),
# and leave the OTHER slot of I (`I0 = ---` or `I1 = ---`) as HALT:
# Then whenever `H1 = 0LI` lands on `I[1]`, `I1 = 0LD` executes the EXACT SAME STEP that `D1 = 0LD` executed in the 8-state machine!!
# AND whenever `H1 = 0LI` lands on `I[0]`, IT HALTS ON `I0 = ---`!!

print("Testing state-splitting (I mimics target state on one bit and HALTS on the other bit)!")
