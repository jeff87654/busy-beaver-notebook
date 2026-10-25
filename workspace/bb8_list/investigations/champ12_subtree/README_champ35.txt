BB(8) NEW CHAMPION CANDIDATE: AN 8-STATE MACHINE BEYOND 2^^^...(35 ARROWS)
=========================================================================

Machine (standard text format, E0 undefined = the halt):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF

Claim (machine-checked in Coq, no axioms):

    The machine halts from the blank tape, and its score (number of 1s on the tape, counting the
    1 written by the halting transition) is

        sigma = 24 * bf + 107,   bf = U 34 (U 34 0)   (U defined below)

    with
        sigma > 2 ↑^35 (2 ↑^35 3)        (35 Knuth up-arrows)
        sigma > 2 ↑^36 3
    and therefore
        sigma > 2 ↑^11 (2 ↑^11 3),

    the bound of the BB(7) champion, which is the listed BB(8) bar (the BB(8) row of the
    bbchallenge Champions table is blank; the BB(7) champion is BB(8)'s default champion).


WHAT THE MACHINE DOES
---------------------
States A-F are identical to Pavel Kropitz's BB(7) champion
1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF; only states G and H differ. It runs the
champion's counter, in Shawn Ligocki's notation B(a; b1, ..., bk):

    configuration  K(ds; a; b) = 0^inf 1 [(01)^(3d+1) 1 for each digit d, farthest first]
                                 (01)^(3a+1) 1 (01)^(3b+1) 1 (01)^2 G> 0^inf

    R1  K(ds; a+1; b)            -> K(ds; a; 2b+2)
    R2  K(.., x+1; 0; b)         -> K(.., x; 2b+2; 0)
    R3  K(.., y+1, 0^k; 0; b)    -> K(.., y, 2b+2, 0^(k-1); 0; 0)     (zero digits are kept)
    R4  K(0^n; 0; b)             halts (n >= 1)

These are exactly the BB(7) champion's rules. The difference is the start: from the blank tape this
machine reaches K(2, 0^34; 0; 0) at step 6,397, a list of 35 digits, where the BB(7) champion
reaches K(2, 0^10; 0; 0) at step 2,117, a list of 11 digits. Each extra digit adds one level of the
recursion, so the score gains 24 Knuth arrows.

Exact value: with U 0 x = 2^(2x+3) - 2 and U (j+1) x = (U j)^(2x+2) (0)  (the counter after
clearing one unit of a digit with j zero digits nearer the counters), the counter is
bf = U 34 (U 34 0) when the 35-digit list becomes all zero, and U j x + 2 >= 2 ↑^(j+1) (2x+3).
The same analysis applied to the BB(7) champion's start (2, 0^10) gives its published bound
2 ↑^11 (2 ↑^11 3), a consistency check.


FILES IN THIS FOLDER
--------------------
BB8_champ35_1RB0RA.v          Coq proof of  Theorem halt : halts tm c0.
                               Rules R1-R4 for all parameters, a lexicographic termination argument,
                               and the 6,397-step start-up.
BB8_champ35_bound.v           Coq proof of the score bounds. Imports the halting file unchanged.
                               Theorems:
                                 sigma_lower_bound        : exists c N, c0 -->* c /\ halted tm c /\
                                                            ones c N /\ arrow 11 2 (arrow 11 2 3) < N
                                 sigma_lower_bound_strong : same with arrow 35 2 (arrow 35 2 3) < N
                                 sigma_gt_arrow36         : same with arrow 36 2 3 < N
                                 score_exact              : ones c (24 * bf + 106) at the halting
                                                            configuration (busycoq stops before the
                                                            halting write, so the score is N + 1)
                               arrow is standard Knuth notation (arrow 0 a b = a*b, arrow 1 a b = a^b,
                               arrow (k+1) a b = (arrow k a)^b (1)); ones c N counts the 1s on the tape.
bb8_champ35_1RB0RA_1LC0RH.md  Report on the halting proof (rules, phases, literal checks, paper bound).
bb8_champ35_bound.md          Report on the bound proof (definitions, proof outline, full probe output).


HOW IT WAS CHECKED
------------------
- Both files compile with Coq 8.20.1 on busycoq (github.com/meithecatte/busycoq, commit bd2e36f),
  using the project's 8-state setup file Individual82.v (logical path BB8).
- The halting file passes our mechanical checker (it matches the declared machine table to the Coq
  table, checks the theorem statement and confirms there are no axioms):
      PASS BB8_champ35_1RB0RA.v: ... HALTS (machine-checked, no axioms)
- For the bound file we compiled an independent probe that prints tm, c0, arrow and ones, the
  theorem statements, and Print Assumptions: every theorem is "Closed under the global context".
- Independently of Coq: literal simulation of the blank-tape run for 5*10^9 steps matched the rules
  at all 51 family configurations reached, and a probe grid (87 rule cases, 42 halting cases) matched.


HOW IT WAS FOUND
----------------
By exhaustive enumeration, not by hand. We enumerated the complete 8-state tree-normal-form subtree
that shares the BB(7) champion's first 8 transitions in first-use order (root
1RB0RA_1LC---_1RD0LB_1RA1LE_---0LC_------_------_------), using mxdys's TNF enumerator and deciders
unchanged (github.com/ccz181078/TM): 67,976,045 nodes, 13,364 holdouts, 8.9 CPU-hours. A digit-list
scanner that recognises the BB(7) champion's structure graded 20 holdouts as champion-type (the
champion's rules, halting when the list is used up). Tracing them from the blank tape: 16 start from
the champion's 11-digit list, 4 start from the 35-digit list. The proved machine is one of the 4; the
other three differ only in G/H transitions and have the same start:
    1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG
    1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LH
    1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC1RH_0LH0RF
(not separately proved). The larger subtree that also frees A1 (about 3*10^9 nodes) is being
enumerated now.


CREDITS
-------
- Pavel Kropitz: the BB(7) champion whose states A-F this machine shares.
- Shawn Ligocki: the analysis of the champion's rules, which this proof follows.
- mxdys: the TNF enumerator and deciders.
- busycoq (meithecatte and contributors): the Coq framework.
- Search, scanning and proofs: this project (Claude Code agents, verified as described above).

October 2026
