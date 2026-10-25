# BB(10) from the BB(8) record's exhaustion: E0 plus free states I, J (bb10_c35_rebuild)

Agent inv-bb10-c35-rebuild, 2026-10-07/08. Tools and data: `bb8_list/investigations/bb10_c35_rebuild/`.

## Verdict

**No f_(ω+1) machine.** The earlier claim for M3 is **retracted**.
- Machine: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA`.
- What the earlier claim missed: in the real run the accumulator entering the second period's unpack stage S2 is far
  smaller than the token being unpacked. The independent verifier inv-bb10-fw1-verify found this.
- In that regime S2 halts at I0 (checked literally, section 3.3). So M3 halts after one full period: **omega-level 1,
  with about four nested clearings at depth ≈ 8 b_f + 50** (2 b_f + 4 = 2↑^37 3).
- That likely exceeds 0LA (depth ≈ 4.8 b_f) but is in the same class. It beats the BB(10) champion and the c35m14
  candidate. Confidence: strong evidence (literal stages plus champion-rule jumps); no Coq.
- The earlier "counter, refill, second counter" picture came from the representative world. That model gives every
  accumulator the same value, so it could not see that S2 compares two accumulators of very different size.

**The best candidates from this base are therefore all omega-level 1:**
1. **The 9-state machine 0LA**, `..._0LI0LC_..._---0LA`, found here first. Session bb8-ab owns its proof and score
   (`../halt_redirect/`). Section 4 is my short independent confirmation.
2. **M3** (section 3): one full cycle plus one full period at depth ≈ 8 b_f, then a halt.
3. **bb8-ab's three-cycle sibling** `..._1LC1RH_0LH0RF_---0LA`.

**Extension searches (omega-level 2 target): negative.**
- 0LA + J: none of 164 extensions rebuilds again (section 5).
- Three-cycle sibling + J: none of 164 halting extensions makes a further full cycle (section 5b).

**General search** (section 6).
- The TNF tree has 219,088 leaves; every leaf that can still halt (17,033) was followed with the mini-follower.
- 309 halt after a full cycle and 954 are infinite rebuilders.
- About 8,200 are unresolved runaways or hit the stage cap.
- The "growth halters" listed there were found in the same representative world and are subject to the same
  caveat. Any stage that compares two accumulators must be re-checked with size-ordered representatives
  (`m3ordered.py`).

## 1. Free slots and the exhaustion configuration

**Slot usage** (`usage.py`). The BB(8) record `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF` reads every slot
except E0 during its 6397-step start-up and inside every R1/R2/R3 phase. So a 10-state extension has exactly five free
slots: E0, I0, I1, J0 and J1.
- E0 must enter I. Otherwise I and J are unreachable and the machine never halts.
- E0 is first read at the record's halting configuration. Every extension therefore runs exactly like the record (Coq)
  up to its first exhaustion K(0^35; 0; b_f), where 2 b_f + 4 = 2↑^37 3.

**Residues.** 2 b_f + 4 is a power of 2 with a huge exponent. Hence b_f ≡ 6 (mod 840), b_f ≡ 16 (mod 25),
b_f ≡ 6 (mod 7, 9, 13) and b_f ≡ 8 (mod 11) (numres.py). Every later tower-type accumulator has the same residues.

**The E0 configuration** after K(0^n; 0; b). It is the Coq term `c_end` of BB8_champ35_bound.v, and was checked
literally for n ∈ {1, 2, 3, 5, 35, 40} and b ∈ {0..7, 18}:

    X(b, n) = 0^inf 101 (011)^(12b+12) [E on 0] 1110101010101010100 (101)^n 0^inf

In D-tokens (D(m) = (10)^m 1): left of the head, D2 D1^(12b+11) D0; right of it, D0 D0 D7 <00> D1^n.

**Base-machine events** (`tokrun.py`, `e0cfg.py`; tokens farthest first, `| a | b` the counters). They hold for every
extension, since they read no free slot:
- far-end D0 + blank: [D0, 0^k | 0 | b] -> [D2, 0^(k+12b+9) | 0 | 0]. The record contains a length-expanding rebuild
  that its own run never triggers.
- far-end D2: it is borrowed like a digit 1 and vanishes.
- residue-0 tokens (D3, D6, D9, ...) are borrowed like digits, down to D0.
- D0 with tokens beyond it blocks the borrow and sends the run to E0, with the configuration
  [.., X−1] E> [D0 D0 D(6b+5) <00> D1^(k+1)].

## 2. Method

1. **TNF enumeration from X(3, 35)** (`enum35.cpp`).
   - E0 over {0LI, 0RI, 1LI, 1RI}; each first-reached I/J slot over 40 values plus halt.
   - 2·10^5 literal steps per leaf; a leaf stops at the first K-moment with ≥ 40 tokens (KLONG).
   - Four Idle processes.

   | E0 | HALT | KLONG | TIME | WIDE | leaves |
   |---|---|---|---|---|---|
   | 0LI | 2,850 | 40,825 | 63,678 | 6,609 | 113,962 |
   | 0RI | 551 | 12,069 | 6,023 | 3,359 | 22,002 |
   | 1LI | 1,578 | 36,259 | 19,034 | 6,211 | 63,082 |
   | 1RI | 502 | 11,274 | 5,416 | 2,850 | 20,042 |
   | total | 5,481 | 100,427 | 94,151 | 19,029 | 219,088 |

2. **Pruning.** A machine with no reachable undefined slot never halts. Only 11,555 KLONG/TIME leaves still have an
   undefined slot, and about 1,100 of those have only unreachable J slots.
   - The 5,478 distinct HALT leaves were re-followed. The enumeration ran at b = 3, but the real class is b ≡ 1 (mod 5)
     and 0LA-type machines halt or rebuild according to b mod 5.
3. **Mini-follower `mf35.py`.** It follows the real run from X(b_f, 35) stage by stage.
   - **Literal stages.** `stage35.exe` runs as a C++ server.
     - It stops at a K-moment whose champion process exceeds a cap (accumulator token > 600) when run abstractly with
       exact integers. Smaller champion phases run literally.
     - It reports the slots read, so a cached stage result is reused by every machine that agrees on them.
   - **Abstract jumps.** follow2.py's `jump()` with numres residues: R1-R3 in r-form, offset e = 1, run to the next
     blocker (D0/D2/D3), a-block or list end.
   - **Representatives.**
     - Every huge accumulator becomes the least representative of its class mod 2520, i.e. b = 6 (r = 19), the class
       of b_f.
     - Exact values above 2000 are also replaced by their class representative.
   - **Termination checks.**
     - LOOP: event configurations repeat in shape with non-decreasing constant increments. A shrinking count is a
       countdown and runs on.
     - A "big jump" crosses ≥ 50 zero digits. The n = 35 lists give ≤ 40, while 12b-type runs at b = 6 give 60-120.
   - **Full-cycle and level tests.**
     - Mode C: start b = 126, which is ≡ 6 (mod 120).
     - Mode G: start b = 846, which is ≡ 6 (mod 840).
     - Mode F: every post-start accumulator at b = 126.
     - A crossed length that changes from A to F after a genuine full cycle means omega-level ≥ 2. A "genuine" cycle
       is one at stage ≤ 3 that crosses ≥ 60 zeros; without that rule, slowly growing countdown runs give false DEP
       flags.
     - Run B (start b = 18 or 30) is **not** a valid full-cycle test. 0LA-type stage 0 depends on b mod 5, and those
       starts are outside the real class (pointed out by bb8-ab). It is not used.
4. **Validation of hits.**
   - follow2.py (period detection, fitting, validation) with the record template.
   - Literal rule checks: `stage0chk.py`, `rulechk.py`, `stage2chk.py`.

## 3. M3 = `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA` (REVISED: omega-level 1)

**Revision (2026-10-08).** The f_(ω+1) claim in earlier messages is withdrawn.
- inv-bb10-fw1-verify pointed out that the S2 table below needs y = 2R + 4 − (x−3)/2 > 0. In the real run the
  accumulator R entering the second period's S2 is far smaller than the token x being unpacked.
- Literally (3.3): for y ≤ −1, S2 halts at I0. So the real run halts at the second period's S2, and the counter
  never runs out.
- Sections 3.1 and 3.2 remain correct as descriptions of the stages. Section 3.3 is the corrected end of the run.

### 3.1 Conventions

**Tokens.** D(m) = (10)^m 1. A configuration is written farthest token first, ending `| a | r`; the head is on the
blank right of the tape in state G.

**K-moment** (the record's family `Kc ds a b`). The tape ends `... D(3a+1) D(r) D2` with r = 3b+1 (tail D2 = 10101).
- **Counters and the r-token.** a and b are the champion counters, and r = 3b+1 is my "r-token". In the stage tables
  "a = 0" means the a-token D1.
- **Map to follow2.** follow2.py's R (template c35, e = 0, tail D4) is read one round later: R = 3b = r − 1.
- **Map to the record.** The BB(8) record's B (2B+4 = 2↑^37 3) is such a b. bb8-ab's universal R = 49612750485498
  equals 3 × 16537583495166, i.e. R = 3B.

**Digits.** D(3d+1) is the digit d, and D1 is a zero. D(3y) and D(3y+2) are borrowed like digits (m -> m−3) down to
D0 / D2. D0 and D2 block a borrow; D3 is borrowed (-> D0).

**Far parts.** F1 = D6^N D3 (first counter) and F2 = D6^N D0 D2 D0 (after the refill), with N = 4b+1 at the start.

**Residues** (`residues.py`, using the lead's stable 2-tower residue T(m)).
- Every accumulator at a stage input is the result of a champion clearing at huge depth. The S4 jump and the refill
  stage are covered too: each ends by refilling 2b+2 and clearing it.
- So 2b+4 = 2^(2b'+4) with b' again a tower: a 2-tower of enormous height. Hence, for EVERY accumulator of the run
  (r1, all period accumulators, r at the end of the first counter, and r' at the refill):

      b ≡ 5046 (mod 27720): b ≡ 8 (11), 6 (8), 0 (3), 1 (5), 6 (7), 6 (9), 16 (25)
      r = 3b+1 ≡ 15139 (mod 27720): r ≡ 3 (11), 3 (8), 1 (3), 4 (5), 5 (7), 1 (9)        follow2's R = 3b ≡ 2 (mod 11)

  This agrees with numres (B ≡ 5046 mod 27720) and with bb8-ab's R ≡ 2 (mod 11).

### 3.2 The run

**Stage 0** (literal, `m3stage0.py`; exact for b = 1..60 and b = 126):

    X(b, 35) -> [D6^(4b+2), D2, D2, D0, D5, 0^(8b+49) | 0 | 1]

**Jump 0** (full cycle). D5 -> D2 at depth 8b+49 gives b1 ≥ A_{8b+48}(2) ≥ 2↑^(8b+50) 3 − 2. Here A_n(D) is the
record's counter after clearing [D, 0^n] from 0 (Coq U_closed: A_n(D)+2 ≥ 2↑^(n+2)(D+1)).

**Stage 1** (literal, `m3stage1.py`, 70 cases):

    [D6^(4b+2), D2, D2, D0, D2, 0^(8b+49) | 0 | R] -> [D6^(4b+1), D3, D(2R+5), D8, 0^(8b+51) | 0 | b-token D2]

The jump that follows is R3 with b-token D2: D8 -> D5, then the refill D9 is borrowed to D6 and D3. That gives the
period start **P(C0 = 2r1+5, x = 5, Z = 8b+50) = F1 [C0, 5, 3] 0^Z | R**. C0 is the counter token; in follow2's
terms it is D(2R1+7), the same value 6b1+7.

**Period map** (literal stages; jumps = Coq R1-R3 plus the checked borrows). P = F [C, x, 3] 0^Z | R.

| stage | literal transition (input -> next jump K-moment) | following jump |
|---|---|---|
| S1 | F [C, x, 3] 0^Z \| R -> F [C, x, 0, 2R+5] 0^(Z−1) \| 0 \| 1 | clear D(2R+5) at depth Z−1; stops at D0 |
| S2 | F [C, x, 0] 0^Z \| R -> F [C−4, 2, 0, 2R+4−(x−3)/2] 0^(Z+x−2) \| 0 \| 1 | clear D(y) (y ≡ 2 mod 3) to D2 at depth Z+x−2 |
| S3 | F [C, 2, 0, 2] 0^Z \| R -> F [C−4, 2R+6, 7] 0^(Z+1) \| 0 \| 1 | clear D7, then D(2R+6) to D2 |
| S4 | F [C, 2] 0^Z \| R -> F [C−3, 2R+6] 0^Z \| 0 \| b-token 2 | R3 with b-token D2: D(2R+6) -> D(2R+3); refill D9 -> D3 |

- **S2** (D0 block -> E0 -> I -> J -> base states) unpacks D(x) into x−2 zero digits. Here x = 2r'+3 was made by the
  previous period's S4 from that period's accumulator r'.
- **Net per period:** P(C, x, Z) -> P(C−11, 2r''+3, Z+x−1). The counter falls by 11, the run grows by 2r'+2, and
  digits ≥ 2 are cleared at depth ≥ x−2 ≥ 2r'. So b_next ≥ A_{2r'}(2) ≥ 2↑^(6b') 3 ≥ f_ω(b').

**Refill** (S2 with C = 0 on F1):

    D6^N D3 [0, x, 0] 0^Z | R  ->  D6^(N−1) D0 D2 D0 [C' = 2R − (x+1)/2, 2, 0, 5] 0^(Z+x+7) | 0 | 1

Then a jump (D5 -> D2) gives S3 on F2 with C = C' = 2r − r' − 2 > 0 (r ≫ r'). The same four maps hold on F2.

**Halt.** S3 with C = 1 on F2 halts in state I reading 0 (I0 undefined).

### 3.3 How the real run ends (corrected)

**S2 has two regimes** (`m3unpack.py`, literal; input F1 [C, x, 0] 0^Z | R):
- **y ≥ 5:** the table in 3.2 holds.
- **y ≤ −1:** the machine halts reading I0, with C untouched. The switch is sharp in the scans for R = 19, 31 and 43
  (y = 5 gives J, y = −1 gives H).
- With real-class sizes R ∈ {19, 91} and x ∈ {1241, 11801}, Z ∈ {3, 10, 25}, C ∈ {30, 704}: halt in every case,
  e.g. R = 19, x = 1241 halts at step 48,516 with 1957 ones.
- R = 355 halts at x = 11801 and continues at x = 1241 (y = 95).

**Sizes in the real run.** All clearings below run at essentially the same depth d ≈ 8 b_f + 50: the first period has
x = 5, so the run grows by only 3.
- **R0**, after the stage-1 jump. This is R3 with b-token D2, so b is reset to 0; then D9 -> D6 -> D3. It is two units
  from a reset: R0 = A_d(2·A_d(2) + 2).
- **Period 1:**
  - R1 = clear D(2R0+5), about (2/3)R0 units;
  - R2 = clear D(2R1+3), about (2/3)R1 units (x = 5, so y = 2R1+3 > 0 and S2 is regular);
  - R3 = clear D7 and D(2R2+6), about (2/3)R2 units;
  - S4 makes x2 = 2R3 + 3, and its jump resets again: R4 = A_d(2·A_d(2) + 2), the same form as R0.
- **Period 2:** S1 gives R5 = clear D(2R4+5), the same construction as R1. So R5 ~ R1, while R3 is two whole levels
  of iteration above it.
- At S2: y = 2R5 + 4 − (x2−3)/2 ≈ 2R1 − R3 < 0, so S2 halts. The S1 clearing that feeds S2 is one level deep; it is
  not deeper than the clearing that made x.

**Ordered-representative run** (`m3ordered.py`; huge accumulators represented in the size order
R0 ~ R4 << R1 ~ R5 << R2 << R3).
- Three variants, e.g. 19 < 31 < 55 < 91. All give: jumps over 97 and 98 zeros (stage 0 and stage 1); period 1 over
  98, 101, 103 and 102 zeros; period 2's S1 over 102 zeros; then HALT at I0 in S2, after 7 jumps.
- The earlier representative runs (FIXREP, m3chain, m3real, endgame) gave all accumulators one value. They therefore
  followed the counter to its refill and second end, which the real run never reaches.

### 3.4 Checks

| file | what | cases | mismatches |
|---|---|---|---|
| `m3stage0.py` | stage 0 from X(b,35), exact form, b = 1..60, 126 | 61 | 0 |
| `m3stage1.py` | stage 1 -> [D6^(4b+1), D3, D(2R+5), D8, ...], b ≤ 61, five R | 70 | 0 |
| `m3rules.py` | S1-S4 on F1 and F2, refill, halt; N ∈ {1,2,4}, C ≤ 30, x ∈ {17..65}, R ∈ {19..91}, Z ∈ {3,8,20,45} | 15,984 | 0 |
| `m3rules2.py` | S4 at C = 3, S1 at C = 0, S2 with x = 5 | 720 | 0 |
| `m3real.py` (+ `m3real_q.py`, r = 5899, 48 cases before it was stopped) | real class: r ∈ {91, 355, 619, 5899} (correct mod {8,3,11}, {8,3,7,11}, {8,3,5,11}, {8,3,5,7,11}), x = 2r+3, N = 1..3, Z = 1..12, 25, 40; both counter end sequences, refill, halt, generic stages | 2,232 (r = 91, 355, 619) + 48 (r = 5899, `m3real_q.py`) | 0 |
| `rulechk.py` | R3 with b-token D2; borrows from tokens 9, 6, 3 (base machine; no I/J slot used) | 2,430 | 0 |
| `endgame.py` | whole period chain from constructed period starts, C = 0..23, all post-start accumulators at r ∈ {19..46} | 240 runs | all odd r halt |
| `m3unpack.py` | S2 with R << x: boundary y = 5 (J) / y = −1 (H); real-class sizes all halt | 3 scans + 36 runs | as stated |
| `m3ordered.py` | whole chain, size-ordered representatives | 3 runs | all halt at period 2's S2 |
| `ktrace.py ... K` (r = 91), `m3chain.py 355` | whole chain, single representative (superseded: equal sizes hide the S2 regime) | 2 runs | refill, then halt |

- **follow2.py** confirms stages 0-6 symbolically. Its stage 7 fails because it samples successive accumulators
  independently: y = 2R7 − R5 + 3 < 0 for samples with R5 > 2R7, whereas in the real run R7 ≫ R5.
- **No fully literal run is possible.** Every instance's first clearing (depth ≥ 8b+49 with b ≥ 1) is
  astronomically long.
- **The representative world.** It is the closest substitute: literal stages and exact abstract jumps, with every
  post-start accumulator set to one value in a chosen residue class. At r = 91 (`ktrace.py`, correct mod 8, 3 and 11)
  the run goes through the first counter 187 -> refill -> C' = 89 = 2·91 − 91 − 2 -> halt at S3(1) in stage 105.

- **What the whole-chain runs are** (`ktrace.py`, `m3chain.py`, `m3ordered.py`). They are hybrid runs, neither a fully
  literal run nor the real blank-tape run.
  - **Start.** A literally constructed X(6, 35), the closed form of the record's E0 configuration after
    K(0^35; 0; 6), checked against literal record runs.
  - **Literal stages.** Every step of the 10-state machine between jump points is simulated literally by
    `stage35.exe`, with no acceleration.
  - **Model jumps.** follow2's `jump()` runs the champion process to the next blocking event. R1-R3 on standard tokens
    are the record's Coq-proved rules. The borrows from residue-0/2 tokens, R3 with b-token D2, and the blocker
    treatment are checked literally (`rulechk.py`, 2430 cases), not proved in Coq.
  - **Representatives.** Each new huge accumulator is replaced by a representative: one value (FIXREP) or a
    size-ordered list (REPSEQ).

### 3.5 Size (corrected)

- The halting tape keeps the token D(x2) (ones ≈ 1.5 x2 in the literal halting runs), so sigma ≳ 3·R3.
- R3 is about four nested levels of clearing at depth d ≈ 8 b_f + 50: roughly f_(d+1)(f_(d+1)(f_(d+1)(f_(d+1)(·)))).
  That is omega-level 1, at index ≈ 8 b_f.
- **Against 0LA** (three levels at depth ≈ 4.8 b_f; `../halt_redirect/`): M3 is very likely larger, since
  f_(d+1)(n) = f_d^n(n) with d ≈ 8 b_f outgrows any fixed iteration of f at index ≈ 4.8 b_f. Same class, though. A
  careful comparison (and Coq) is open.
- **Against the BB(10) champion** (sigma ≤ 2↑^(K+1) K + 4, K ≤ 2↑^28 26) and **the c35m14 candidate** (2↑^L 5,
  L = 4·2↑^27 3 + 17): both far below.

## 4. 0LA: independent confirmation (short; the full treatment is in ../halt_redirect/)

Tokens are listed farthest first; real class b ≡ 1 (mod 5); Z = (24b+196)/5.

| stage | configuration and transition | how checked |
|---|---|---|
| 0 (literal) | X(b, 35) -> [D9^((12b+8)/5), D11, 0^Z \| a=0 \| b-token D2] in exactly (49104 b² + 321612 b + 228984)/25 steps | `stage0chk.py`: b = 1, 6, ..., 101, all exact (logs/stage0chk.log); mf35 modes A (b=6), C (b=126), G (b=846) |
| jump 0 | R3 with b-token D2 refills D9 (2·2+5); the borrows D9->D6->D3 each refill 2b+2 and clear it at depth Z−2: b1' = A_{Z-2}(2) ≥ 2↑^Z 3 − 2, b2' = A_{Z-2}(2b1'+2) | `rulechk.py`: 2430 cases, 0 mismatches (R3 with b-token D2; R3/R2 from tokens 9, 6, 3 in front of D9^N D8; depths ≤ 300) |
| 1 (literal) | D3 -> D0, refill 2b2'+2 | `rulechk.py` |
| jump 1 | clear that digit at depth Z−2: b3' = A_{Z-2}(2b2'+2) ≥ 2↑^(Z+2) 3 − 2; the borrow stops at the D0 | Coq R1-R3 |
| 2 (literal) | [D9^N, D8, D0, 0^(Z−1) \| 0 \| b3'] -> E0 -> I -> 0LA ... -> state I reading 0 (halt) | `stage2chk.py`: N ∈ {1,3,16}, k = 1..129, r ∈ {1,19,43,91}: halts for every k except k = 7 (real k = Z−1 is huge); ones = 2r + c(k,N) |

- **Notation.** A_n(D) is the counter after clearing [D, 0^n] from b = 0. The record's bound A_n(D)+2 ≥ 2↑^(n+2)(D+1)
  comes from its Coq `U_closed` (BB8_champ35_exact.v).
- **follow2.py** (`logs/cand1_follow2.log`) agrees independently: period 5, two full cycles, omega-level 1, then
  `HALT ... ones = 2*R2+744/25*b+2121/25`, state (I, 0).
- **Score:** sigma ≥ b3' ≥ 2↑^(Z+2) 3 − 2, with Z = (12·(2↑^37 3) + 148)/5.
- **Comparisons.** These are in `../halt_redirect/score_comparison.md`, which bounds the champion by an arrow count
  ≤ 2↑^27 49. My own estimate from Uc_le (U_j(x) ≤ 2↑^(j+2)(2x+4)) agrees: sigma_champion ≤ 2↑^(K+1) K + 4 with
  K = 3b1/4 + 6 ≤ 2↑^28 26, far below.
- `follow2.py --blank` does not lock onto the 35-digit family from the blank tape. The start is covered by the record's
  Coq proof instead.
- **Tools:**
  - `stage35.exe` (literal stages);
  - `mf35.py MACHINE --mode ACFG` (the stage chain at several representatives);
  - `stage0chk.py`, `rulechk.py`, `stage2chk.py` (literal checks);
  - `tokrun.py` (any token configuration to its next K-moment).

## 5. Extensions of 0LA by state J (the omega-level-2 target)

`ola_j.py` (output `ola_j.tsv`, log `ola_j.log`).
- **The space.**
  - 0LA's slots are all fixed except its halt I0, and J is reachable only through I0. So I0 ∈ {0LJ, 0RJ, 1LJ, 1RJ}.
  - J0 and J1 are branched TNF-style when the real run first reads them, with the other one left as the halt.
  - That gives 4 + 160 machines.
  - The other 36 values of I0 leave J unreachable, so those machines never halt.
- **How the run was followed.**
  - Each run starts from X(6, 35). Stages 0-1 are 0LA's and cached.
  - The redirect happens at 0LA's stage-2 halting configuration with the real-class lengths: m' = 67 ≡ (24 b_f + 191)/5
    (mod 4032), accumulators at r = 19.
  - Up to 300 stages and 2·10^7 literal steps per stage.

| outcome | count | what happens after the redirect |
|---|---|---|
| HALT | 37 | at once (stage 3), or one small stage later; the score is 0LA's plus a little |
| LOOP | 7 | periodic small-depth processes (≤ 6 zeros crossed) |
| MAXSTAGES (300) | 16 | periodic small-depth processes (≤ 23 zeros crossed), periods > 8 |
| TIME / WIDE | 43 / 59 | literal runaways right after the redirect; spot checks show growing junk counters or a fixed extent |

- **No run makes a jump across ≥ 50 zeros after 0LA's halting point.** A second rebuild from 0LA's accumulator R2 would
  show crossings of about 12·6+c in this representation. So there is no omega-level-2 machine in this space.
- **Why.** At the redirect the tape holds the old structure, R2 as a b-token, and the old zero run already rewritten
  into (001)-type junk by the stage-2 routine. With only two new transitions, none of the 164 routines turns it back
  into a champion list.

## 5b. Extensions of bb8-ab's three-cycle sibling by state J

The base is the 9-state machine `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA`, i.e. the 35-digit
F/H-relay sibling with E0 = 0LI and I = (halt, 0LA). Script `sib_j.py` (output `sib_j.tsv`, log `sib_j.log`).

**Follower.** The generalised follower `mf35g.py` (family SIB) runs with the generalised stage server `stage35g.exe`.
- **K-moment:** state F reading 0 at the right end, the tape ending in a token followed by the tail 10101010; the
  accumulator token is D(3b) (e = 0), as in follow2's template R,F,P=1,u=01,s=1,d=3d+1,b=3b+0,S=10101010.
- **Start:** the base machine's configuration at its first E0 read after K(0^35; 0; 6).
- **Calibration:**
  - mf35g on the 9-state sibling reproduces bb8-ab's chain: two jumps over 67 zeros, the stage-2 rebuild to 108
    zeros, two jumps over 108 zeros, then a halt at I0.
  - On the record family it reproduces 0LA.
  - The K detection was checked on constructed configurations: R1 r -> 2r+6, and R2/R3 refill 2r+7, with e = 0.

**Space.** As for 0LA: I0 ∈ {0LJ, 0RJ, 1LJ, 1RJ}, then J0/J1 branched as reached, with one left as the halt. That is
164 machines, up to 300 stages and 2·10^7 literal steps per stage.

| outcome | count | notes |
|---|---|---|
| HALT | 37 | 35 at the redirect stage, 2 one tiny stage later (crossings ≤ 1); score ≈ the base's |
| LOOP | 1 | |
| MAXSTAGES (300) | 42 | periodic processes, several crossing 60-214 zeros per period (e.g. `0RJ0LA_0RG---`, `0RJ0LA_1LA---`); none halts within 300 stages |
| TIME / WIDE | 39 / 45 | literal runaways after the redirect |

**Result.** No halting extension of the three-cycle sibling performs a further full cycle. The large-crossing
MAXSTAGES machines are repeating cycles. Their undefined J slot is not read in 300 stages, so they are non-halting
in all likelihood. Strictly they are unresolved: they would need a residue-correct end analysis like M3's.

## 6. General search results (all 17,033 leaves that can still halt; `mf_rest.tsv`)

Mini-follower in mode A, up to 300 stages and 10^6 literal steps per stage, for:
- the 11,555 KLONG/TIME leaves with an undefined slot;
- the 5,478 distinct HALT leaves, which were re-followed in the real class.

| outcome | without a full cycle | after ≥ 1 full cycle (≥ 50 zeros crossed) |
|---|---|---|
| HALT | 7,185 | 309 |
| LOOP (non-decreasing affine repetition) | 219 | 954 |
| MAXSTAGES (300) | 435 | 410 |
| TIME / WIDE (literal runaway) | 5,803 / 924 | 603 / 94 |
| FAIL (jump recursion on long lists) | 0 | 97 |

- **The 954 LOOPs after full cycles** are infinite rebuilders in the style of the c35m14 "loopers". Example:
  `..._0RI0LC_..._---0LJ_1RJ0LF` rebuilds [D2, 0^(12b+n+27)] at every exhaustion and does not depend on n mod 840.
- **Level screen** (`levelchk2.py`, `levels2.tsv`). 158 of the 309 halters-after-cycles were re-run with every
  post-start accumulator at b = 126:
  - 109 unchanged: omega-level 1, comparable to or below 0LA;
  - 27 changed before any full cycle: harmless;
  - 22 changed after a full cycle. These include M3 and the countdown machines below.
- **Growth halters** (`growth_halters.txt`, `growthchk.py`): the crossing depth grows by steps that scale with the
  accumulator representative (r = 19 vs r = 31). This is the single-representative world, where every accumulator has
  the same value. M3's growth turned out to be an artifact of that model (section 3.3), and the others need the same
  size-ordered re-check.

  | machine (E0, I, J) | growth per period | end |
  |---|---|---|
  | 1LI, ---0LJ, 0LD0RA (**M3**) | 2r+2 per period in the model; the real run halts at period 2's S2 | halt I0 (section 3.3) |
  | 1LI, ---0LJ, 0LE0LJ and 1LI, 0LJ0LI, ---0LC | (4r+5)/3 per period, 38 stages at both r, count probably ∝ b | halt I0 / J0 |
  | 1LI, 1LJ0RI, {0RB, 0RH, 1RG}--- | two steps of about 4r+35 | halt J1 |
  | 1RI, 0LJ0LI, ---0RC | one step of 2r+2, then an r-dependent count | halt J0 |
  | 1LI, ---0RJ, 1RH0RI / 1RH0RJ; 1LI, ---1LJ, 1RH0RJ; 1LI, ---1LJ, 1LA0RJ | small (+1..+4) or WIDE at r = 31 | halt at r = 19 |

- **9-state machines** (J unused): only 0LA (E0 = 0LI, I1 = 0LA) halts after a full cycle. The others halt after
  n = 35-type crossings of at most 43 zeros.
- **Countdown machines.** Example: `..._0LI0LC_..._---0LJ_0RJ0LG`, where follow2 confirms the structure stage by stage.
  - It counts a token D(2R1+1−3i) down while its near run grows by 2 per stage.
  - The final depth is about 4R1/3 with R1 ≈ b_f: omega-level 1, below 0LA.

**Coverage gaps.**
- The TNF tree was branched at b = 3, not in the real class. Slots that are first read only at b = 6 would show up as
  HALT rows; second-level branching of those rows was not done, except for 0LA (section 5).
- TIME/WIDE leaves (about 7,400) and MAXSTAGES leaves (845) are unresolved. Spot checks show runaways and cyclers.
- The level screen covered 158 of the 309 halters-after-cycles.
- **Representative world.** The mini-follower assumes each stage behaves uniformly in its huge parameters
  (representatives mod 2520). It misjudges (a) behaviour that depends on residues mod 11, 13, ..., and (b) stages
  that COMPARE two accumulators, because single-value representatives make every accumulator equal. Case (b)
  is what invalidated M3's f_(ω+1) reading (section 3.3).

## 7. Reproduction (in `bb8_list/investigations/bb10_c35_rebuild/`)

**Build.** `g++ -O2 -std=c++17 -static -o X.exe X.cpp` (MSYS2 ucrt64) for enum35, stage35, grade35 and chain35.
`hyb10.cpp` is a copy of `../bb10_bb7_descendants/hyb10.cpp`, built locally for the local copies of `follow2.py` and
`numres.py`.

**Enumeration.** `enum35.exe 35 3 200000 30000 40 E0,...,...,...,...` for E0 ∈ {0LI, 0RI, 1LI, 1RI}, at Idle
priority, gives `e_<E0>.txt`.

**Mini-follower.** `mf35.py` drives the `stage35.exe -s` server. Modes:
- A: b = 6 and r = 19 mod 2520, the real class;
- C: b = 126;
- G: b = 846;
- F: later accumulators at b = 126;
- `FIXREP`: a fixed r for every later accumulator.

Commands:
- one machine: `python mf35.py MACHINE --mode A --stages 300 --maxs 300000000 -v`;
- batches: `python mf_batch.py SET OUT.tsv WORKERS 300 1000000`, with sets `set_partial.txt` and `set_queue2.txt`
  (output `mf_rest.tsv`);
- 0LA + J: `python ola_j.py ola_j.tsv`;
- level screen: `python levelchk2.py halt_big.txt mf_rest.tsv levels2.tsv`;
- growth: `python growthchk.py` (reads `growth_halters.txt`).

**M3 checks** (each prints its case count and mismatches):
- `python residues.py` (tower residues and the conventions);
- `python m3stage0.py`;
- `python m3stage1.py`;
- `python m3stage1r.py` (stage 1 in the real class);
- `python m3rules.py` (log `logs/m3rules.log`);
- `python m3rules2.py`;
- `python m3real.py` (real-class end-game grid; log `logs/m3real.log`);
- `python endgame.py 3 20 0 23 19 22 25 28 31 34 37 40 43 46`;
- `python ktrace.py M3 K 200 0 60` prints the refill and the halt (whole chain at r = 91);
- `python m3chain.py 355` (whole chain at r = 355);
- `python m3unpack.py` (S2 with R << x: the halting regime);
- `python m3ordered.py` (whole chain with size-ordered representatives: halt at period 2's S2);
- follow2: `logs/m3_follow2.log`.

**Other families.** `python mf35g.py FAMILY MACHINE`, with FAMILY = REC or SIB, uses the server
`stage35g.exe` (built from `stage35g.cpp`). Three-cycle sibling + J: `python sib_j.py sib_j.tsv`.

**0LA checks:**
- `python stage0chk.py 102` (logs/stage0chk.log);
- `python rulechk.py`;
- `python stage2chk.py`;
- `logs/cand1_follow2.log`, `logs/cand1_b846.log`.

**Helpers:**
- `tokrun.py`: a token configuration to its next K-moment;
- `e0cfg.py`: E0 configurations of base events;
- `m3probe.py`: literal stage probe;
- `usage.py`: slot usage;
- `e0probe.py`: X(b, n);
- `grade35.cpp` / `chain35.cpp`: early graders, superseded by mf35.

## 8. Open questions

1. **M3 vs 0LA.** A careful size comparison (both omega-level 1; M3 has the larger depth), and Coq for M3's short
   chain: stages 0 and 1, one period, and S2 in the halting regime.
2. **The other growth halters** in section 6 (e.g. `..._---0LJ_0LE0LJ`). Their growth was seen with one representative
   for all accumulators, and any stage comparing two accumulators must be re-run with size-ordered representatives
   (`m3ordered.py`). They are probably omega-level 1 like M3.
3. **Second-level TNF branching.** HALT rows of the mini-follower at slots first read in the real class. Children with
   a remaining undefined slot could do still more.
   - Also unresolved: the 42 large-crossing MAXSTAGES extensions of the three-cycle sibling (section 5b).
4. **Unresolved leaves.** About 7,400 TIME/WIDE and 845 MAXSTAGES leaves.
5. **The BB(7)-champion analogue** (E0 plus H, I, J free from the champion's own exhaustion) was not run. M3's
   mechanism (a counter plus unpacking the accumulator token) might also exist there.
