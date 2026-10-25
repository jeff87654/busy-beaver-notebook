# dl:016582 NOBOUNDARY machine 1RB1LB_0RC---_1RD1RG_0LE0RH_1LF1LE_0RD0RA_1RB0LE_1RC0LD

Investigator: inv-016582 (Opus 5.5, bb8-investigator workflow), 2026-10-08. Scratch scripts are in this folder.

## Verdict

**Never halts. Confidence: STRONG EVIDENCE, not proved.** There is no check.py PASS. The only halting transition is B1.

- **Not a record.** The machine is an exponential counter: the tape grows by 3 cells per cycle and each cycle costs about (2+sqrt 2) times
  more steps.
- **What is proved.** proofs/BB8_016582_1RB1LB.v (partial) compiles (python build.py, ~21 s). It proves the machine-level rewriting
  rules (R12, R3(m), R4(m), the sweeps) and the start-up. It has NO nonhalt theorem.
- **What remains.** Everything is reduced to one general lemma (Y). Its mutual partner (C) is verified numerically but not proved.
  See "Remaining gap".

## 1. F-turn rewriting system (exact, all m, any context)

- State F is entered only by E0 -> 1LF. F always writes 0 and moves right. An **F-turn configuration** is state F about to read
  the head cell [F].
- Between two F-turns the machine performs exactly one of these rewrites. Tape order is left to right; only the shown cells are read.

| rule | rewrite | what happens |
|---|---|---|
| R12 | x [F] a 1 1 -> [F] x 1 a 0 | bounded; the head moves 1 cell left |
| R3(m) | [F] 1 1 (001)^m 0000 -> 0 (110)^m 1 [F] 1110 | B C G sweep over (010)^(m+1) |
| R4(0) | [F] 0 1 000 -> [F] 0 1 1 1 0 | |
| R4(m+1) | [F] 0 1 (001)^(m+1) 000 -> 0 0 (110)^m 1 [F] 11110 | D H C sweep over (100)^(m+1) |

How the rules were checked:
- They were found by micro.py, which records every F-turn to F-turn segment of the real run.
- rulechk.py checks them literally for m <= 40, with random left and right contexts: 0 mismatches, and the context is never touched.
- They are proved in Coq for all m, with symbolic sides (lemmas R12, R3, R4_0, R4).

## 2. Canonical abstract system (canon.py)

An F-turn configuration has three parts:
- **L**: the bits left of the head. It is a stack, and a pop from blank gives 0.
- **P**: the prefix at the head, one of 111, 011, 11, 01. The forms 1111, 11101 and 0111 are 111 or 011 with first gap 0 or 1.
- **G**: the gaps of the right side, 0^g 1 each. It is a stack, and an exhausted stack counts as an infinite gap.

The rules on (L, P, G):
- (111,g) pop x: (x11, g+1).
- (011,g) pop x: (x1, g+2).
- (11, 2^m h R), h >= 4: push 0 T^m 1 (T = 110), giving (111, (h-3) R).
- (01, 2^m h R), h >= 3: if m = 0, (011, 0 (h-2) R). If m >= 1, push 00 T^(m-1) 1, giving (111, 0 (h-2) R).
- Stuck (possible halting) cases: R3 with h <= 3, R4 with h <= 2, and (111,0) popping a 0.

How the abstract system was checked:
- cmpabs.py: it equals the TM on **150,000 consecutive F-turns**, from TM step 744 on.
- absim.cpp: it ran **3e9 abstract steps** with no stuck case, through S(19).
- The abstract step counts between consecutive S(k) satisfy exactly a(n) = 4a(n-1) - 2a(n-2), whose roots are 2 +- sqrt 2.

## 3. Configuration families and rules

Families:
- S(k) = 0^inf [F] (010)^k 0^inf. Here L is empty and the state is (01, 2^(k-1)). The TM reaches S(4) at step 221.
  The left-extension times are S(5) 724, S(6) 2443, S(7) 8314, S(8) 28361.
- X(c,G) = 0^inf T^c 1 [111,(0,G)]. On the tape this is 0^inf (110)^c 1 [F] 1111 ...
- E(H): L empty, P = 11, gap list H.
- With an arbitrary left part beta in front, the same families are written beta X, beta E, and so on.

Rules. All were verified on the abstract system (xrules.py, ytest.py, ctest.py): random beta, random a, random G (odd and even),
j, m <= 6, c <= 8.

| rule | statement | notes |
|---|---|---|
| **(A)** | X(c,G) -> X(0,(2c,G)), c >= 1 | 14, 42, 138, 466, 1586, ... abstract steps |
| **(B)** | X(0,(2^j,h,R)) -> X(j+1,(h-2,R)) for even h >= 4; X(0,(2^j)) -> X(j+1,()) | finite steps; passes through S(j+3) in the second case |
| **(Y)** | beta T^j 1 [111,(a,G)] -> beta [11,(2^(j-1), a+5, G)], j >= 1, any beta, a >= 0, G | beta is never read |
| **(E1)** | beta [11,(2^j,h,G)] -> beta 0 [11,(2^(j-1),h+2,G)] | (E1) = R3 + (Y) |
| **(C)** | beta T [11,(2^m,h,G)] -> beta [11,(2^(m+1),h,G)], h >= 5 | 20, 68, 232, 792, ... steps; fails for h = 4 |

How the rules fit together:
- **(Y) by induction.** Y(j) = Y(j-1) (with base beta T), followed by C(j-2), for j >= 2. Y(1) is 7 concrete steps.
- **(A) from (Y).** X(c,G) = Y(c,0,G). Then (E1)^(c-1) gives E(2c+3, G) over a base 0^(c-1). Six finite steps then give X(0,(2c,G)).
- **Top level.** Starting from S(k), the orbit is the gap-list game (2^j, h, R) -> (2j+2, h-2, R), and (2^j) -> (2j+2) starts a
  new cycle.
  - Every entry stays **even and >= 2**, so the first non-2 entry is always >= 4. Hence (A) and (B) always apply and the run never
    gets stuck.
  - Example from X(3): (6), (2,4), (4,2), (2,2,2), then the next cycle X(4). This matches the TM (X(c,j) -> X(c-1,j+1), S(k) -> X(k-2,0)).

So **non-halting follows from (C)** (then Y, E1, A, B, and the even-gap invariant).

## 4. Remaining gap / plan for the proof

1. **Prove (C)**, by mutual induction with (Y). C(m) calls Y(m), (E1)-chains, the base-zero-consuming (B)-type steps, (A) with c = 1,
   a (B') branch, and Y(m+1). Here (B') is the base ...100, where the third pop is a 1 and R3 is used instead of R4.
   - Run cdec.py m h to print C(m) as a chain of E-forms and Y-forms with the base shown (B = beta).
   - The difficulty is that C(m) plays the gap game on a base of zeros beta T 0^m and consumes the base. A clean statement probably
     needs a lemma for "gap game over base beta T 0^k".
2. **Encode the abstract layer on tapes and finish the proof.**
   - L is a list of symbols on the left side. P and G become P *> gaps G *> const 0.
   - Derive the canonical steps from R12/R3/R4.
   - Prove (Y), (C), (A), (B), then the even-gap invariant, then progress_nonhalt.
3. The machine-level layer is already done in the .v file.

## 5. Automatic methods that failed

All runs were short or at Idle priority.

| method | settings | result |
|---|---|---|
| ngcps2 (plain n-gram CPS) | nL/nR up to 30 (4/24 ... 28/16) | fails within seconds (B1). The halting path is a B C G sweep over a long (010)^n whose end is forgotten |
| ngann (writer annotations, g) | ANN 1/2/3, g on/off, machine and mirror, windows 4..12 | fails immediately |
| tctl (run-length token CTL, m7 folder) | | spurious B1 via a far-end anchor |
| tok/ngtok.cpp (new) | token-run side folds 1^a 0^b with merged counts, H <= 4, caps up to 8/12, counts mod 2, start from S(4) | always reaches spurious B1 or the 30-40M config cap. It is compatible with the generic Coq checker nonhalt_of_check (fold = any N -> N -> N) if a closing parameter set is ever found |
| macrocps.py (n-gram on the abstract system, D-run / T-run tokens) | windows up to 8/6 | stuck at (01,(D,1,D)), which comes from a spurious (01, 2^m 5) |

Why these fail: odd gaps (5, 7, ...) occur legitimately inside (Y)/(C), and they are safe only in the P = 11 context. With P = 01 the
gap after a 2-run is never 5 (m >= 1), and never 3 or 5 when m = 0. That correlation lies across an unbounded 2-run and the left stack.

## Reproduction

    cd bb8_list/investigations/bb8_016582_1RB1LB0RC
    python micro.py 2000000      # observed F-turn rewrites
    python rulechk.py            # literal rule check, m <= 40, random contexts
    python cmpabs.py 744 150000  # abstract system == TM on 150k F-turns
    absim.exe 3000000000         # abstract run, S(k) times, no stuck
    python xrules.py; python ytest.py; python ctest.py   # rules A, B, Y, E1, C
    cd ../../proofs && python build.py BB8_016582_1RB1LB.v   # partial Coq (compiles; no nonhalt theorem)
