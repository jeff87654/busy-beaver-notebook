# n1 `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC`: machine-checked halting and score

Opus investigator (inv-n1-coq), 2026-10-08. Scratch and generators: `bb10_n1_coq/` (resume notes in NOTES.md).

## Verdict
- **HALTS, machine-checked.** `proofs/BB10_n1.v`, `Theorem halt : halts tm c0.` check.py (run from bb8_list/proofs):

      PASS BB10_n1.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC HALTS (machine-checked, no axioms)

- **Score, machine-checked.** `proofs/BB10_n1_bound.v` imports the halting file unchanged. It proves:
  - the exact ones count at the halt;
  - the verifier's bound sigma > G^N(33);
  - that n1 beats the BB(10) champion and the 10-state candidate 0LJ0LC, each against its own proved exact score.

  Every theorem prints "Closed under the global context".
- **The stage chain of bb10_n1_verify.md is correct.** No correction was needed, and the Coq proof follows it event
  by event. The only real residue used is T = 2 mod 7 (B = 6 mod 7), proved in Coq.
- **Class f_(omega+1).** Let T = 2^(37 arrows) 3 and F n = 2^(n arrows) 4 = 2^(n+1 arrows) 3. The final zero block
  is at least F^N(34), with N = (6T-19)/7 = (12B+5)/7 growth events.

## 1. Statements (printed by Coq; probe `bb10_n1_coq/probe_bound.v`, log `probe_bound.log`)

    halt : halts tm c0
    score_exact : exists c f k w, c0 -->* c /\ halted tm c /\ ones c (2 * w + f + 3 * k + 22) /\
                  iter (2 * JJ + 1) F 34 <= w
    sigma_lower_bound : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\
                  iter ((6 * arrow 37 2 3 - 19) / 7) (fun x => arrow (x + 1) 2 3) 33 < N
    dominates : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\
                  forall K x, K <= F (F (F 34)) -> x <= F (F (F 34)) -> iter x (arrow K 2) x < N
    beats_M3_bound : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\
                  arrow (4 * arrow 37 2 3 + 41) 2 (arrow (4 * arrow 37 2 3 + 39) 2 (arrow (4 * arrow 37 2 3 + 35) 2 5)) < N
    beats_lead : exists cl nl co no, c0 -[ BB10_lead_1RB0RA.tm ]->* cl /\ halted BB10_lead_1RB0RA.tm cl /\
                  BB10_lead_bound.ones cl nl /\ c0 -->* co /\ halted tm co /\ ones co no /\ nl + 1 < no + 1
    beats_champion : exists cc nc co no, c0 -[ BB10_champion_1RB1RA.tm ]->* cc /\ halted BB10_champion_1RB1RA.tm cc /\
                  BB10_champion_bound.ones cc nc /\ c0 -->* co /\ halted tm co /\ ones co no /\ nc + 1 < no + 1
    arrow_agree : forall k a b, BB10_lead_bound.arrow k a b = arrow k a b

**Definitions.**
- arrow 0 a b = a*b and arrow (S k) a b = (arrow k a)^b (1), as in BB8_champ35_bound.v.
- F n = arrow n 2 4.
- T = proj1_sig T_sig, with T_def : T = arrow 37 2 3 (sealed).
- JJ = (3T - 13)/7.
- `ones c N` means the tape holds exactly N ones (the definition of BB8_champ35_bound.v).

**Halt convention.** The halt is in state J reading 0 (J0 undefined), so the standard score is N + 1.

How the comparisons work:
- **0LJ0LC** (BB10_lead_bound.score_exact). Its count is Nl = 2 b2 + 2L + 5, with b2 + 4 = arrow L 2 5,
  L = 4 bf + 33 and bf + 4 = arrow 27 2 3. Coq proves Nl < arrow (L+2) 2 4 <= F (F (F 34)) <= F^N(34) < N.
- **BB(10) champion** (BB10_champion_bound.score_exact, Nc = b2c + 3). BB10_lead_vs_champion.b2c_le gives
  b2c <= b2 of 0LJ0LC, so Nc < Nl < N.
- **M3.** Its files prove only lower bounds (BB10_fw1_bound.sigma_lower_bound, index 4T+41).
  - Coq proves N exceeds that expression (`beats_M3_bound`).
  - `dominates`: N exceeds every (2^(K arrows))^x (x) with K, x <= F(F(F 34)). F(F(F 34)) is far above 4T+41, so this
    covers any M3 upper bound that is a bounded nesting of arrows at index 4T + c.
  - A machine-checked "n1 > M3" still needs an upper bound for M3's score, and no file provides one yet.

## 2. Structure

B-form, in the verifier's notation: `Bf L ts A` = L D(t_1)..D(t_n) D(0) D(A) H> 0^inf, with D(m) = (10)^m 1 and ts
nearest-first.

| piece | statement (verifier's notation) | how |
|---|---|---|
| PASS, PRO, R2M | doubling round; R1 prologue; R2 borrow | generated (mexp.py) |
| R1 | [L,t+3\|A] -> [L,t\|2A+8] | PRO + (A+3) PASSes |
| CLR | [L,c+3d,1^n\|A] -> [L,c,1^n\|(U n)^d(A)] | induction on n, d (A = 1 mod 3) |
| H | [1^(n+1)\|a] -> [2,1^(2a+4),0,1^n\|6] | generated |
| S0 | [2,1^(M+5),0,1^(n+2)\|a] -> [2,5,1^M,0,0,0,a+3,1^n\|4] | generated |
| P1 | [2^k,5,1^(m+6),0,0,2,1^n\|a] -> [2^(k+2),5,1^m,0,0,0,1,a+3,1^n\|6] | generated |
| P2 | [2^k,5,1^(m+6),0,0,0,1,1+3p,0,1^(w+1)\|r+1] -> FarP + [2,r+2,1^(w+2p+2)\|4] | generated |
| P3 | FarP k m + [2,2,1^w\|a] -> [2^(k+2),5,1^m,0,0,a+5,1^w\|6] | generated |
| P4 | [2^k,5,1^(m+2),0,0,3q,0,1^(w+1)\|r+1] -> [2^k,5,1^m,0,0,r+2,1^(w+2q+2)\|4] | generated |
| E | [2^(k+6),5,1,0,0,0,1,1+3p,0,1^(w+1)\|r+1] -> FarE k + [r+3,1^(w+2p+2)\|4] | generated |
| HALT | FarE k + [0,1^w\|f] -> J reading 0 | generated |
| PERIOD | Per k (m+14) n a -->* Per (k+4) m n2 a2, with n2 >= F(F n) | by hand (main.v.in) |
| ENDGAME | Per (k+4) 7 n a -->* FarE k + [0,1^w\|f], with w >= F n | by hand |

The table uses three shapes:
- Per k m n a = [2^k,5,1^m,0,0,2,1^n|a];
- FarP k m = "00" D0^3 D1^m D5 D2^(k+2);
- FarE k = a fixed 44-cell tail followed by D2^k.

The run:
1. c0 -->* [7,1^35|4] in 6447 steps.
2. -->* [1^36|Af], with Af = 3T - 8.
3. -->* H, S0, R2 + CLR(9) at depth 33, P4 with Q = 0, CLR.
4. -->* Per 1 (6T-19) 34 a.
5. JJ periods follow, because 6T - 19 = 14 JJ + 7 when T = 2 mod 7.
6. ENDGAME, then HALT.

Arithmetic in Coq:
- U j (3a+1) + 8 = 3 * arrow j 2 (a+3), so U n 4 + 8 = 3 F n.
- Af = (U 35)^2 (4) = 3T - 8.
- T = 2^2^2^y with y >= 1, hence T = 2 mod 7.
- Each Per satisfies the invariant a = 1 mod 3 and a >= U n 4. So every P2 and P4 adds at least F(depth) - 3 zeros.

## 3. Compile cost (Idle priority, shared PC)

| part | time |
|---|---|
| machine part alone (dev/M.v, 322 KB, first build) | 857 s |
| final halting file BB10_n1.v (353 KB) | 489 s |
| check.py on BB10_n1.v (recompiles) | about 8 min |
| bound file BB10_n1_bound.v | 43 s |

mexp.py generates all machine lemmas in 2 s. My token use was about 0.5M.

## 4. Lessons
- **Validate every spec literally first.** A wrong target makes mexp.explore search forever; check each spec with
  `drv.py NAME lit`.
- **Encode positivity in the spec.** When the engine splits the run behind the head, write values known to be
  >= 1 as r+1 or w+1 in the spec. Marking them positive does not help.
- **Match the engine's run shapes in targets.** Write (101101)^p for 1^(2p), placed where the engine puts it.
  finish_norm handles alignment rotations but not block regrouping.
- **Scopes.** Individual102 opens sym_scope, so 0 and 1 are Sym. The abstract part opens nat_scope and marks tape
  terms with %sym.
- **Rewrite arrow_0 only with explicit instances.** A bare `rewrite arrow_0` misfires on a*b subterms.
- **Seal Af.** It had to be sealed as proj1_sig of a Qed-proved sig. Unsealed, an f_equal/lia goal unfolded it, and
  the compile reached 21 GB before I killed it.
- **Never `replace` a numeral.** It also rewrites inside larger numerals (7 occurs inside 35).
- **Avoid `simpl iter`.** It unfolds F; use `change (iter (S n) F x) with (F (iter n F x))`.
- **bnorm must interleave.** It has to alternate `cbn [lfr]` with the lfr rewrites.

## 5. Reproduce
    cd bb8_list/investigations/bb10_n1_coq
    python gen_final.py ../../proofs/BB10_n1.v          # 2 s
    python coqc_idle.py ../../proofs/BB10_n1.v 30000     # about 8 min at Idle
    python gen_bound.py ../../proofs/BB10_n1_bound.v && python coqc_idle.py ../../proofs/BB10_n1_bound.v
    cd ../../proofs && python check.py BB10_n1.v

## 6. Open gaps
- **M3.** There is no machine-checked comparison with M3's actual score, because no file proves an upper bound for
  it. n1 dominates M3's proved lower bound and every arrow iterate at index up to F(F(F 34)).
- **Exact value.** The bound states w >= F^N(34), not the full exact value, which involves the clearing outputs. That
  is enough for every comparison.

## 7. Closed-form score (proofs/BB10_n1_exact.v, added 2026-10-08)

`proofs/BB10_n1_exact.v` imports BB10_n1.v and BB10_n1_bound.v unchanged. It compiles in 23 s at Idle, and every
Print Assumptions gives "Closed under the global context". Statements (printed by Coq; probe
`bb10_n1_coq/probe_exact.v`, log `probe_exact.log`):

    score_closed_unfolded : exists c, c0 -->* c /\ halted tm c /\
      ones c (let J := (3 * arrow 37 2 3 - 13) / 7 in
              let s := stepn J (34, arrow 35 2 (arrow 34 2 5 - 1)) in
              let W := fst s + 2 * snd s - 6 in
              2 * W + 3 * arrow (S W) 2 (arrow (fst s) 2 5) + 12 * J + 5)
    score_closed   : exists c, c0 -->* c /\ halted tm c /\ ones c score_value     (the same value, named)
    score_value_gt : iter (2 * JJ + 1) F 34 < score_value      (above the lower bound of BB10_n1_bound.v)

with the period map

    step (n, g) = let n2 := n + 2 * g - 6 in
                  let n4 := n2 + 2 * arrow (S n2) 2 (arrow n 2 5 - 1) - 4 in
                  (n4, arrow (S n4) 2 (arrow n2 2 5 - 1))
    stepn 0 s = s,   stepn (S j) s = stepn j (step s).

**Notation for the formula.**
- At a period start, n is the zero-block length.
- g encodes the accumulator a as a = 3g - 8.
- J is the number of full periods.

**The score.** The halt is in state J reading 0, so the standard score is the closed form + 1.

**What made it closed.** Every clearing in the run starts from the accumulator 4, and
(U j)^d (4) = 3 * 2^(j+1 arrows) (d + 2) - 8 (lemma iterU). Consequences:
- A deposited 9 cleared at depth n - 1 gives the transit 3 * 2^(n arrows) 5 - 8.
- That transit, cleared to D2 at the new depth n2, gives the accumulator 3 * 2^(n2+1 arrows) (2^(n arrows) 5 - 1) - 8.

The P2 and P4 growths add 2(a/3) + 2 zeros each, which gives the two lines of `step`.

**The other pieces.**
- **Start state.** (34, g0), with g0 = 2^(35 arrows) (2^(34 arrows) 5 - 1). This is stage 0, then CLR(9) at depth 33, then P4 with Q = 0, then CLR at depth 34.
- **Endgame.** The final zero block is W = n + 2g - 6. The final accumulator is 3 * 2^(W+1 arrows) (2^(n arrows) 5) - 8.
- **Ones count.** It is 2W + f + 3k + 22 with k = 4J - 3, which gives the expression above.

**Proof method.** The proof repeats the period and endgame scripts of BB10_n1.v with explicit witnesses:
- PERIOD_U and PERIOD_G give the exact period.
- PERIODS_G iterates it with the invariant g >= F n, and n grows by F twice per period.
- ENDGAME_G and reach_per_exact give the exact endgame and start.

**What "closed" means here.** The score is one explicit expression in arrow, iterated by `stepn` J times. It
cannot collapse further, because every period feeds its accumulator into the next arrow index. It is the
f_(omega+1) recursion itself, written as a primitive recursion of arrows. The number of iterations,
J = (3T - 13)/7, is the only place the BB(8) record's T = 2^(37 arrows) 3 enters.

**Lesson.** A `set` variable that abbreviates a closed arrow term, here x0 := arrow 34 2 5 - 3, made a later
`apply` unfold it and evaluate. The compile hung. Use `remember ... eqn:` for closed huge values.

## 8. Fast-growing hierarchy level and Graham's number (proofs/BB10_n1_fgh.v, added 2026-10-08)

`proofs/BB10_n1_fgh.v` imports BB10_n1.v, BB10_n1_bound.v and BB10_n1_exact.v unchanged. It compiles in 41 s at
Idle. Print Assumptions gives "Closed under the global context" for all five theorems. The definitions below are
printed by Coq (probe `bb10_n1_coq/probe_fgh.v`, log `probe_fgh.log`):

    fgh 0 n = S n,  fgh (S k) n = Nat.iter n (fgh k) n        (f_k)
    f_omega n = fgh n n,   f_omega1 n = Nat.iter n f_omega n   (f_omega, f_(omega+1))
    up3 0 n = 3 * n,  up3 (S k) n = Nat.iter n (up3 k) 1     (up3 k n = 3 ^(k arrows) n)
    graham_g 0 = 4,  graham_g (S k) = up3 (graham_g k) 3    (graham_g 1 = 3^^^^3, ..., g_64)
    Graham = graham_g 64
    arrow 0 a b = a * b,  arrow (S k) a b = Nat.iter b (arrow k a) 1

The file also checks small values with `reflexivity`: fgh 1 5 = 10, fgh 2 3 = 24, up3 1 4 = 81, up3 2 2 = 27.

Statements, with `ones c N` meaning the halting tape holds exactly N ones (the standard score is N + 1):

    fgh_level : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\
                f_omega1 ((3 * arrow 37 2 3 - 13) / 7 - 2) < N < f_omega1 (6 * arrow 37 2 3)
    fgh_lower : ... /\ f_omega1 ((3 * arrow 37 2 3 - 13) / 7 - 2) < N
    fgh_lower_64 : ... /\ f_omega1 64 < N
    graham_lt_f_omega1_64 : Graham < f_omega1 64
    beats_graham : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ Graham < N

So n1 sits at level omega+1 exactly. Its score lies between f_(omega+1)(J - 2) and f_(omega+1)(6T), with
T = 2^(37 arrows) 3 and J = (3T - 13)/7, the number of periods. Both bounds hold for the same N, the exact count of
score_closed.

How the bounds are proved:
- **Upper bound for f_k.** fgh k n <= 2^(k+2 arrows) (3n) for n >= 3. From this, f_omega x <= F(F x) with
  F n = 2^(n arrows) 4.
- **Lower bound.** f_omega^j(m) <= F^(2j)(m). The run gives N > F^(2J+1)(34), from score_value_gt and score_ge.
- **Upper bound for n1.** It uses the arrow lower bound 2^(k arrows) n <= fgh (k+1) n and the monotonicity of fgh in
  both arguments. With them, 2^(k arrows) z <= f_omega(k + z + 1), f_omega(y+1) >= 2 f_omega(y), and
  f_omega(y) >= 4y for y >= 2. One period then grows the size x = 2(n+g) + 6 to at most f_omega^8(x) (step_bound).
  The start is at most f_omega^2(43). The final expression of score_closed is below f_omega^(8J+7)(12J+48), which is
  at most f_omega1(12J+48), which is at most f_omega1(6T).
- **Graham.** 3^(k arrows) n <= 2^(k arrows) (2n) and f_omega(x) >= 2^(x-1 arrows) x give
  graham_g j < f_omega^j(64) by induction on j.

Lesson: `rewrite` with a lemma such as fgh 0 n = S n or n + 0 = n rewrites only the instance it matches first.
Use explicit instances, or `!` where several instances need rewriting.
