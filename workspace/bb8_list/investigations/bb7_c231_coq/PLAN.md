# Coq plan: champ_231 / champ_232 (BB(7) Ackermann-type digit list)

Machines: 231 = 1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB, 232 = same with G0 = 1LC.
busycoq bd2e36f (bb9_f3_coq/ext/busycoq/verify), 7-state instance BB72/Individual72 copied from bb8_list/proofs.

## Configuration (busycoq tape), digits nearest-first
  Kc ds a b = const 0 {{E}}> 0 >> [1]^^(S (2b)) *> 0 >> 0 >> [1]^^(2a) *> 0 >> 0 >> rgt ds
  rgt []     = 1 >> const 0
  rgt (d::t) = [1]^^(2d) *> 0 >> 0 >> rgt t
Literal-checked (tools/rules.py, both machines): blank -> Kc (1^20) 1 2 at step 3715 (231).

## Macro rules (all literal-checked before proving)
  R1ITER : Kc ds a b -->* Kc ds 0 (b + 3a)                 (2a mini-cycles MC: E>0 1^p 00 1 r -> E>0 1^(p+3) 00 r)
  R23    : k <= b -> Kc (0^k ++ S y :: t) 0 b -->+ const0 E> 0 1 00 (1100)^k 1^(2(b+3-k)) 00 rgt (y::t)
           k=0: = Kc (y::t) (b+3) 0 (R2);  k=S k': = Kc (1^k' ++ (b+2-k') :: y :: t) 1 0 (R3)
           micro: START, FW^(2k+1) (forward passes), TURN, BW^k (backward passes), FINB
  R4x    : k <= b -> Kc (0^k) 0 b -->* c_end (C reading 1, C1 undefined), ones c_end = 2b+7
           micro: START, FW^(2k+1), TURN4, FWZ^(2b+4-2k) (passes into blank), END2, BW^(b+2-k), FIN
  (k <= b is needed: block at TURN has 2b+3-2k cells, TURN needs >= 2.)

## Abstract part (as in BB8_champ35_bound.v)
  X ds b := Kc ds 0 b.  U 0 x = 3x+9 (R2 then R1ITER);
  U (S j) x = iter (x+2-j) (U j) (W j 3),  W 0 B = B,  W (S j) B = U j (W j B)
  (R3 at depth j+1 writes 1^j ++ [x+2-j] with a=1 -> b=3, then clear depth 0..j.)  Defined by a pair fixpoint.
  CDP : j <= B -> X (0^j ++ v :: Us) B -->* X (0^(S j) ++ Us) (iter v (U j) B)   (strong induction on j, then v)
  Side facts: U j x >= x+1, W j B >= B + j (so every R3/R4 meets k <= b).
  Run: c0 -->* Kc (1^20) 1 2 -->* X (1^20) 5 -->* X (0^20) (W 20 5) -->* c_end, sigma = ones = 2 * W 20 5 + 7.
  Descent is implicit: the clearing recursion is structural (no lexicographic order needed).

## Score chain
  arrow k a b Knuth (arrow 0 a b = a*b).  U (S j) x >= arrow (S j) 3 (x+3-j) style bounds, monotonicity.
  Targets: arrow 20 3 2 < N, arrow 19 3 (arrow 18 3 3) < N (or best honest nesting),
  c231_beats_bb7_champion : 3 * arrow 13 2 3 + 22 < N  (champion sigma, bb8_champ35_vs_bb7/COMPARISON.md)
  and arrow 11 2 (arrow 11 2 3) < N (wiki bound).  Never compute closed arrow/U/W terms (Opaque, generalize).

## Files
  C231.v (machine 231 rules + run + exact score), C232.v (generated from the same template, G0 = 1LC),
  Bound.v (machine independent: U/W lower bounds, arrows), probe.v (string parser, Print Assumptions).
  coqc at Idle via tools/cq.py, PIDs in pids.txt.
