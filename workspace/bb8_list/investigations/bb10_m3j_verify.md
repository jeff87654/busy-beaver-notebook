# M3J = M3 with J = 1LD1LC: independent check (inv-bb10-fw1-verify, 2026-10-08)

Machine M3J: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_1LD1LC`.
It is the BB(8) record with E0 = 1LI, I = ---0LJ and J = 1LD1LC.
Tools: `bb8_list/investigations/bb10_m3j_verify/` (my M3 tools, re-pointed to M3J).
Notation as in `bb10_fw1_verify.md`:
- B-form [t1..tn | A] = tape D(t1)..D(tn) D0 D(A) G>, with D(m) = (10)^m 1;
- 2B + 4 = 2↑^37 3 is the record's final counter;
- deep accumulators have raw A ≡ 0 (8), 1 (3), 8 (11), 0 (25).

## Verdict

**M3J HALTS in state I reading 0 after 6 macro clearings, i.e. bb8-ab's 11 jumps. It is ω-level 1, NOT ω-level 2.**
- Every clearing crosses only the zero block made by stage 0, of length z = (24B+201)/5 ≈ 2.4·(2↑^37 3).
  bb8-ab's own logs agree: zeros = 67..71 at b = 6 for every jump, under std, big and shrink.
- **Why the "list length" grows.** It is parked pair lists, (D0 D3)^k and (D1 D0)^k with k ∝ an accumulator, sitting
  behind D0 blockers. No borrow scan ever crosses them; the specials remove at most 9 pairs.
- **No size-order dependence** (the M3 failure mode is absent here).
  - With J = 1LD1LC, the unpack of a token does not spend the transit.
  - Every special is checked with both size orders, and whole chains with 30 random fake orders have identical
    structure.
- **Size:** 2↑^(z+4) 5 < σ < 2↑^(z+4) 6, i.e. one f_ω-scale application at index ≈ 2.4·(2↑^37 3).
  - The largest term is the parked token D(F4+3) from the clearing at depth z+3.
  - Corrected after bb8-ab's cross-check (section 3).
  - My first version said F4 ≪ F6, which is wrong; its upper bound 2↑^(z+3) 5 was wrong too.
- **Ranking** (paper level, each step conditional on the other machine's own chain):

      M3 (> 2↑^(8B+56) 4) > bb8-ab's 3-cycle sibling (≈ z+37 arrows) > M3J > 0LA (< 2↑^(z+1) 4) > 0LJ0LC > BB(10) champion

- **Status: strong evidence, no Coq.** All specials are literal-checked parametric rules, the clearings are the
  record's R1/R2, and the halting special halted in every check (w = 1..60 with three (Y, A) pairs, plus 30
  real-class runs).

## 1. The chain (real run; `chain_j.py`, `realj.py`)

**Stage 0** (literal, from the record end [1^36 | 6B+4]):
- H: [2, 1^(12B+12), 0, 1^35 | 6]. Same as M3; no E0 is read.
- TL5, (12B+8)/5 times. Each step eats 5 D1 per E0: D2 → D12, then [9^j, 12] → [9^(j+1), 12]; the zero block grows
  by 2.
- TLE (the real 12B+12 ≡ 4 mod 5): [9^j, 12, 1^4, 0, 1^z | 6] → [9^(j+1), 11, 1^(z+2) | 6].
- Result: [9^((12B+8)/5), 11, 1^z | 6] with z = (24B+201)/5.

**Then:**

| # | step | result (P = 9^n prefix) |
|---|---|---|
| J1 | R2 (deposit 9), CLR(9): 3 units at depth z−1 | [P, 8, 0, 1^(z−1) \| F1] |
| Sa | blocked borrow at D0 (left token D8) | [P', 5, 3, 0, 3, F1+1, 1^(z+1) \| 6] |
| J2 | R2, CLR(9) at depth z | [.., 3, F1−2, 0, 1^z \| F2] |
| Sb | unpack of D(F1−2): [.., 5,3,0,3, X, 0, 1^w \| A] → [.., 2,7,0,0,3,3, (0 3)^((X−10)/4), 0, A+1, 1^(w+2) \| 6], for any A | parked (0 3)^((F1−12)/4) |
| J3 | R2, CLR(9) at depth z+1 | [.., 0, F2−2, 0, 1^(z+1) \| F3] |
| Sc | unpack of D(F2−2): [.., (0 3)^m, 0, X, 0, 1^w \| A] → [.., (0 3)^(m−2), 0,0,5, (1 0)^((X−4)/2), 0,1, A+3, 1,0, 1^(w−1) \| 6] | parked (1 0)^((F2−6)/2) |
| Sd | [.., (1 0)^p, 0,1, Y, 1,0, 1^w \| 6] → [.., (1 0)^(p−9), 0,1,4,1,1,1,0,3,0, Y+8, 0, 1^(w+2) \| 6] | 9 pairs used |
| Se | unpack of D(F3+11): [.., 0,1,4,1,1,1,0,3,0, Y, 0, 1^w \| 6] → [.., 0,1,1,7,1,1,0,3,3, (0 3)^((Y−11)/4), 0, 7, 1^(w+2) \| 6] | parked (0 3)^(F3/4) |
| J4 | R2 (D7 → D4, deposit 9), CLR(9) at depth z+3 | [.., (0 3)^n, 0, 4, 0, 1^w \| F4] |
| Sf | [.., (0 3)^n, 0,4,0, 1^w \| A] → [.., (0 3)^(n−2), 0,0,5,0,1, A+3, 1,0, 1^(w−1) \| 6] | |
| Sg | [.., (0 3)^n, 0,0,5,0,1, Y, 1,0, 1^w \| 6] → [.., (0 3)^(n−1), 0,2,1,1, Y, 1^4, 0,0,9, 1^(w−2) \| 4] | |
| J5 | CLR(9) at depth z | [.., Y, 1^4, 0,0,0, 1^w \| F5], F5 = F2 |
| Sh | [.., Y, 1^4, 0,0,0, 1^w \| A] → [.., Y, 1,0,1, A+1, 1^(w+1) \| 4] | |
| J6 | CLR(F5+1 ≡ 2 → D2) at depth z+1: (F5−1)/3 units | [.., 2,1,1, F4+3, 1,0,1, 2, 1^(z+1) \| F6] |
| Si | D2 scan → **HALT** (I reads 0) | |

**Residue conditions used.**
- The unpack rules need X ≡ 2 (mod 4) for Sb and Sc, and Y ≡ 3 (mod 4) for Se.
- In the real run X = F − 2 and Y = F3 + 11 with F ≡ A_deep ≡ 0 (mod 8), so both hold.
- Stage 0 needs 12B + 12 ≡ 4 (mod 5); the real B ≡ 1 (mod 5).

## 2. Checks

- **Rules** (`rules_j.py`): TL5, TLE, Sa, Sb, Sc, Sd, Se, Sf, Sg and Sh.
  - 160 random literal instances each (60 + 100), 0 mismatches.
  - A ranges over small values and real-class values up to ~800, X and Y up to ~300, with both orders (A ≪ X and
    A ≫ X).
  - Three predictor bugs in my first script (TLE, Se, Sh) were fixed and re-checked; the machine was never at fault.
- **Order independence** (`chain_j.py -grid`): 30 whole chains from the record end.
  - B ∈ {1, 6, 11}, fakes ≡ 40 (mod 120) in random order.
  - All give the same sequence of specials and clearings, and all HALT at Si.
  - `osim.py` with increasing and decreasing fakes gives the same.
- **The halt, Si** (`si_scan.py`, `si_real.py`).
  - w = 1..60 with three (Y, A) pairs, plus 30 real-class runs (w ≡ 118 mod 120, Y and A random in both orders): all
    HALT at I0.
  - The ones count has period 5 in w. In the real class (w = (24B+206)/5 ≡ 3 mod 5, from B ≡ 16 mod 25) it is exactly
    ones = Y/2 + A/2 + 9w/5 + c, with 0 misfits over the 30 runs.
- **Real-class whole chains** (`realj.py`): B = 366 (≡ B mod 600, so w is in the real class), random fakes. All HALT.
  The exact ones formula is in section 3.

## 3. Size

**Values.** In Ligocki units a = (F−1)/3, with g_k(x) = 2↑^k(x+3) − 3 at depth k:
- f1 = g_{z−1}^3(1);
- f2 = f5 = g_z^3(1);
- f3 = g_{z+1}^3(1);
- f4 = g_{z+3}^3(1);
- f6 = g_{z+1}^{f5}(1).

**Exact values.** By (2↑^k)^n(2↑^(k+1) m) = 2↑^(k+1)(m+n) and 4 = 2↑^(k+1) 2:
- f1 + 3 = 2↑^z 5;
- f2 + 3 = f5 + 3 = 2↑^(z+1) 5;
- f3 + 3 = 2↑^(z+2) 5;
- **f4 + 3 = 2↑^(z+4) 5**;
- f6 + 3 = 2↑^(z+2)(2↑^(z+1)(5) − 1).

**Real size order: F1 < F2 = F5 < F3 < F6 < F4.**
- f6 + 3 < 2↑^(z+2)(2↑^(z+2) 4) = 2↑^(z+3) 4 < 2↑^(z+4) 5 = f4 + 3.
- So the clearing with 3 units at depth z+3 beats the clearing with f5 units at depth z+1.
- I first wrote F4 ≪ F6, which is wrong.
- The run itself does not depend on the order (section 2).

**Ones at the halt** (real class). Exact fit over 13 real-class whole chains at B = 366 (`fitr.py`), with 0 misfits
(6 runs beyond the 7 that fix the coefficients):

    ones = (5/4)F1 + (3/2)F2 + (5/4)F3 + (1/2)F4 + 0·F5 + (1/2)F6 + c(B),   c(366) = 12023

- The coefficients match the one-at-a-time deltas measured at B = 1.
- A run with fakes ordered F1 < F2 = F5 < F3 < F4 < F6 at B = 366 (`chj_real_order.txt`; the real order has F4 > F6, but
  the run is order-independent):
  - its clearings cross exactly z−1, z, z+1, z+3, z, z+1 zeros, with z = 1797;
  - it HALTs with 17,263 ones, matching the formula.
- The same fakes at B = 966 (≡ B mod 600; z = 4677; clearings at z−1..z+3 again) give 36,847 ones. So, from these two
  real-class points, c(B) = (816B + 1919)/25.
- In the real run F5 = F2, so

      σ_ones = F6/2 + F4/2 + (5/4)(F1 + F3) + (3/2)F2 + (816B + 1919)/25.
- Standard score: +1 if the halt writes a 1.

**Bounds.**
- Lower: σ ≥ F4/2 = (3·(2↑^(z+4) 5) − 8)/2 > 2↑^(z+4) 5.
- Upper: every other term is below F4. So σ < 3·F4 < 2↑^(z+4) 6, because 2↑^(z+4) 6 ≥ 2^(2↑^(z+4) 5).
- Hence

      2↑^(z+4) 5 < σ < 2↑^(z+4) 6,   z = (12·(2↑^37 3) + 153)/5 = m + 2 with m = (24B+191)/5.

**Cross-check.** bb8-ab's independent check of M3J's G/H twin (halt_redirect/v_1LD1LC.md) agrees:
- 11 jumps, then a halt at I0, ω-level 1, parked lists;
- its largest token is D(2R8+5) with 2·b8 + 4 = 2↑^(m+6) 5, which is my f4 + 3 = 2↑^(z+4) 5;
- same bounds 2↑^(m+6) 5 < σ < 2↑^(m+6) 6;
- its size order R1 < … < R8, R9 ~ R3, R10 = R4, R11 between R6 and R8 matches mine (its R8 = my F4).

**Comparisons** (paper level):
- **M3:** σ_M3 > 2↑^(8B+56) 4, and 8B + 56 − (z+5) ≈ 3.2B. So M3 ≫ M3J.
- **bb8-ab's 3-cycle sibling `..._1LC1RH_0LH0RF_---0LA`.** Its jump 3 clears a rebuilt list D4^(m+40), m ≈ z − 2,
  so about z+37 arrows. That is above M3J, by far.
- **0LA.** Its two clearings sit at depth ≤ k+2 = z−1. Its own upper estimate is σ_0LA < 2↑^(z+1) 4 (see
  bb10_fw1_verify.md §5b), so M3J (> 2↑^(z+4) 5) > 0LA by about three arrows.
- **0LJ0LC:** L = 4·(2↑^27 3) + 17 ≪ z, so it is far below. The BB(10) champion is lower still.

## 4. On the "ω-level 2" reading

The screens' "total list length" (2627 and 10233 under 'big', 2673 under 'shrink') counts the parked pair lists, and
those grow with the accumulators.
- A pair list (D0 D3)^k or (D1 D0)^k is not a run of zeros.
  - Each D0 blocks the borrow.
  - Each D3 is worth only one unit.
  - The only specials that touch these lists are Sc (2 pairs), Sd (9 pairs), Sf (2 pairs) and Sg (1 pair).
- So no clearing ever has depth ∝ an accumulator. The crossing depth (the screens' own `zeros=` column) stays at the
  level-1 value z + O(1) in all three policies.

## 5. Reproduction (`bb10_m3j_verify/`)

**Commands.**
- `python rules_j.py 100 23` (rule checks);
- `python chain_j.py 1 1240,2440,...` (one whole chain, verbose);
- `python chain_j.py -grid SEED N` (random fake orders);
- `python realj.py SEED 366 N` (real class);
- `python si_scan.py 61`; `python si_real.py` (the halting special);
- `python osim.py LIST:A F1,...` (ordered-fake discovery);
- `python probe.py 'LIST:A' ...` (one literal special).

**Logs** are in `tmp/`:
- `rules_j*.txt`, `chgrid*.txt`, `realj366*.txt`, `si_real.txt`, `os*.txt`.
