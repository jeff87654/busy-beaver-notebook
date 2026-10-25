# C10: nonhalting proof through a two-counter recurrence

**Status:** C10 is nonhalting. The C-branch proof was completed independently by the audit agent using the P/R sweep lemmas below; the D/E lemmas and strict interval invariant complete the proof. Exact simulation of 667 lemma instances passed as a transcription check. This is a mathematical induction proof, not a conclusion from simulation cutoffs.

C10 is line 10 of discovery_holdouts.txt:

    1RB1LA_0LA0RC_1RA1LD_0LE1RZ_1LC1LF_1RG0LE_1LD1RH_0RE0RG

For all configurations below, place the listed finite word on blank tape and put H on the blank immediately to its right:

    D(n): 1^n
    E(n): 1^n 01
    C(a,b): 1^4 (01)^a 0 1^b 01

Here b is a positive odd integer. Blank tape reaches D(8) at step 39, then C(2,1) at step 71.

## Universal C-branch rules

Let d=(b+9)/2.

- C(0,b) halts in b+14 steps, leaving (b+15)/2 ones.
- If a>=d, C(a,b) -> C(a-d,2b+11) in (3b^2+36b+121)/2 steps.
- If 1<=a<d, C(a,b) -> E(3b-2a+21) in 3a^2-(3b+42)a+(9b^2+156b+683)/4 steps.

The direct universal derivation is supplied by the P/R lemmas below and expanded in candidate_audit_c10.md. The initial grid is in candidate_theory_c10_rules.json, and 357 additional boundary-focused checks passed in candidate_theory_c10_branch_checks.json. These ordinary cell-by-cell checks catch transcription errors; the sweep argument establishes the universally quantified rules.

## Universal P/R sweep lemmas

Define P(u,k,v) by the finite word

    1111 (01)^u (01)^k 1 (01)^v 1,

with E scanning the last 1 of the prefix 1111(01)^u. Define R(k,v) by the finite word

    1111 (01)^k 1 (01)^v 1,

with H scanning the cell immediately after the prefix 1111. Here u,v>=0 and k>=1. The transition-table sweep derivations give:

- C(a,b), a>0, -> P(a-1,1,(b+3)/2) in b+14 steps.
- P(u,k,v), u,v>=1, -> P(u-1,k+2,v-1) in 6k+8 steps.
- P(u,k,0), u>=1, -> the word 1111(01)^(u-1)1^(2k+2)01 with H on its right blank, in 4k+5 steps. For u=1 this is E(2k+6); for u>=2 it is C(u-2,2k+3).
- P(0,k,v) -> R(k+2,v) in 19 steps.
- R(k,v), v>=1, -> R(k+3,v-1) in 6k+22 steps.
- R(k,0) -> E(2k+4) in 4k+2 steps.

For the interior P rule, the exact instruction sequence is (E1,F0,G1,H0)^k followed by E1,F0,G1,H1,G0,D0 and then (E1,F1)^(k+1). The first sweep fills the middle pairs while moving right; the three-instruction H1,G0,D0 turn reverses into the alternating left sweep. This consumes one pair from each side and adds two pairs to the middle, in 4k+6+2k+2=6k+8 steps. The conditions u,v>=1 supply the boundary symbols read in these finite turns.

For the R rule, 4k instructions convert the leading pairs while moving right. H1,G0,D0 reverse the head; 2k+4 leftward E1,F1 instructions form the new alternating block. E0,C0,A1,A1 reach the left blank, then the fixed 11-step A-boundary path described below restarts the right sweep. This establishes R(k,v)->R(k+3,v-1). The v=0 exit fills all leading pairs and finishes with H1,G1, producing E(2k+4).

Starting with v=(b+3)/2, apply the P interior rule until u or v is zero. If a>=d=(b+9)/2, v reaches zero with u>=2, giving the continuing C rule. If a=d-1, the u=1,v=0 exit gives E directly. If 1<=a<=d-2, u reaches zero, and the R rules give E(3b-2a+21). These cases cover every positive a. For a=0, the initial 11-step entry and b alternating F1/E1 steps reach E on the separator before the b-block; E0,C1,D1 halt. This proves the stated halting branch as well.

## Universal D/E lemmas

For even n>=4:

    D(n) -> C(n/2-2,1)       in 2n+16 steps
    E(n) -> D(n+10)          in 6n+51 steps.

For D(n), H0,E0,C0 create two adjacent ones immediately beyond the old block. A1 sweeps across all n+2 ones; after n+5 total steps A reads the blank just left of them. The fixed 11-step boundary path

    A0 B1 C1 D0 E1 F0 G1 H0 E1 F0 G1

ends with H scanning the third of the original ones. It leaves four ones to the left of that head. The n remaining ones are consumed in n/2 repetitions of H1,G1, making (01)^(n/2). H then reads the right blank. This gives C(n/2-2,1), with 2n+16 steps in total.

For E(n), the first 11 instructions

    H0 E0 C0 A1 A1 A1 A0 B1 C1 D0 E1

leave F on the last of the original n ones, with tape 1^(n+1)011. The n alternating F1/E1 steps sweep those n ones into (10)^(n/2). F0 adds one leftmost one and turns right. Repetitions of G1,H0,E1,F0 fill each 10 pair, including the following separator pair. The five-step tail G1,H1,G0,D0,E1 reaches the auxiliary configuration Q(n+2) after a total of 3n+21 steps.

Define Q(a) for even a>=4 as word 1^(a+2)01 with F scanning zero-based cell a. Then

    Q(a) -> D(a+8)           in 3a+24 steps.

To prove Q, sweep the a+1 ones at and left of F with alternating F1/E1 steps. E then scans the blank on the left. E0,C0,A1,A1 reach the next blank to the left, in state A. Apply the same fixed 11-step boundary path above. This leaves four ones followed by H scanning the first zero of (01)^(a/2+2). Every repetition of H0,E1,F0,G1 fills one 01 pair. The head finally enters H on the right blank with a+8 ones. Counting gives (a+1)+4+11+(2a+8)=3a+24.

Combining the E entry with Q(n+2) gives (3n+21)+(3n+30)=6n+51 and D(n+10).

## Strict interval invariant proves nonhalting

Each return to C(a,1) has odd b=1. After j applications of the first continuing C rule,

    b_j = 12*2^j-11,
    a_j = a - [6*2^j-j-6].

Set S_j=6*2^j-j-6. Hitting a=S_j is exactly the conjectured halting branch. If S_j<a<S_(j+1), the residual branch and the D/E lemmas instead give

    a' = 24*2^j-9-j-a,

with b reset to 1. For integer a in this open interval,

    12*2^j-1 <= a' <= 18*2^j-4.

These bounds lie strictly between S_(j+1) and S_(j+2), because their margins are j+6 and 6*2^j-j-4, respectively, both positive for j>=0. Thus each return moves into the next interval and never reaches a halting boundary. The initial a=2 lies strictly between S_0=0 and S_1=5.

The resulting outer sequence is explicitly

    a_j = [32*2^j - 2j - 17 - 7*(-1)^j]/4,

starting 2,13,25,60,120,251,503,1018,... . Every macro segment is finite and follows the universal Turing-machine sweep lemmas; every return lies strictly inside the next safe interval. Thus the blank-tape trajectory continues forever and never executes D1, its only halt instruction.

The complete primitive-lemma transcription check is candidate_theory_c10_certificate.py; its 667 passing cases and classification are recorded in candidate_theory_c10_certificate.json. The supporting independent sweep derivation is candidate_audit_c10.md.

