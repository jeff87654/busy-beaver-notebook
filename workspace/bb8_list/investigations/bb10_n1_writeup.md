# n1: a 10-state machine at the f_(ω+1) level

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC

Write-up by inv-bb10-n1-writeup, 2026-10-08, in the style of the bbchallenge wiki page for the BB(7) champion
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF`. It contains no new results. Every formula is taken from the Coq
files or the verifier reports listed in section 6, or I re-checked it with my own literal simulator
(`bb10_n1_writeup_chk.py`, section 6.3).

| | |
|---|---|
| States | 10 (A–J). One undefined transition, J0, which is the halt. |
| Halts? | **Yes, machine-checked** (`proofs/BB10_n1.v`, `Theorem halt : halts tm c0`, check.py PASS, clean-room rebuild OK). |
| Score | Exactly 2W + f + 3k + 22 ones on the tape when J reads 0, with W ≥ F^(2J+1)(34). Coq-checked (`score_exact`). In closed form, 2W + 3·2↑^(W+1)(2↑^n 5) + 12J + 5, with (n, W) from the period map of section 4. Also Coq-checked (`score_closed`). Add 1 for the standard convention (the halting transition writes a 1). |
| Lower bound | σ > G^N(33), where G(x) = 2↑^(x+1) 3, N = (6T − 19)/7 and T = 2↑^37 3. Coq-checked (`sigma_lower_bound`). |
| Class | f_(ω+1). Roughly f_(ω+1)(0.86·2↑^37 3). This reading is on paper. |
| Beats the BB(10) champion? | **Yes, machine-checked** (`beats_champion`). |
| Found by | bb8-ab's grow-and-count selector search (`halt_redirect/selector.md` §6b). |

Notation used throughout: T = 2↑^37 3. B is the BB(8) record's final counter, defined by 2B + 4 = T. F(n) = 2↑^n 4,
which equals 2↑^(n+1) 3. Knuth arrows: 2↑^0 x = 2x, 2↑^1 x = 2^x, and 2↑^(k+1) x = 2↑^k 2↑^k … 2 (x twos).

---

## 1. Overview (no Turing-machine background needed)

**What is being measured.** A Turing machine works on an infinite strip of cells, each holding 0 or 1. It has a small
finite memory (its "state", here one of ten letters A–J) and a read/write head. At every step it reads the cell under
the head, then follows a fixed rule table: write a bit, move one cell left or right, switch state. The table has one
deliberately missing entry (state J reading a 0). The machine stops when it hits that entry. The Busy Beaver game
asks which 10-state table that eventually stops leaves the most 1s on the strip. n1 is a candidate.

**The number system on the tape.** n1 never stores numbers in binary. It writes blocks D(m) = 1 (01)^m, which encode
m. Blocks are separated by their own 1s, with no gaps. The tape then reads as a list of digits plus one "accumulator"
at the right end, where the head sits. A digit d is the block D(3d+1), so D(1) is the digit 0. Write v = (A+8)/3 for
the accumulator block A; v is the "value". The machine's basic move is the one used by the current BB(7) and BB(8)
champions. It lowers the nearest nonzero digit by one, with an effect on v that depends on that digit's depth (how
many zero digits lie between it and the head):

> **Removing one unit from a digit at depth j turns v into 2↑^j v.**

At depth 0 this doubles v. At depth 1 it maps v to 2^v. At depth 2 it gives a tower of v twos, and so on. Emptying a
whole list in this way is an Ackermann-type computation. The BB(8) record uses it on a list of 35 zero digits behind a
leading digit 2, and finishes with v = 2↑^37 3.

**Phase 1: the BB(8) record's computation.** The first eight states of n1 are a close relative of the BB(8) record
(its "G/H sibling", one of the four 35-digit machines of the record family). For more than 2↑^37 3 steps, n1 does
exactly what the record does. After 6447 steps it has the list "digit 2, then 35 zeros". It clears that list and reaches the
moment when every digit is 0, with v = T = 2↑^37 3. Here the record halts. n1 does not.

**Phase 2: turning T into a countdown.** At this moment n1 rewrites its value as a unary counter: a block of about 6T
zero digits, parked at the far left of the tape. It also starts a second list, the "zero list", of 34 zeros next to
the head. The counter is fenced off by blocker blocks (D0 and D2), which the Ackermann move cannot cross. So the
counter is never used as digits. It is only decremented, by 14 per period.

**Phase 3: the periods.** The rest of the run is a loop of about 0.43T periods (exactly (3T − 13)/7). Each period
runs the same sequence of events, and the zero list grows twice per period:
1. The current huge value v is parked as a single block in front of the zero list.
2. A small fresh value is cleared at the current depth n. It becomes a huge new value, a tower-like number of
   height about n.
3. The parked block is unpacked into about 2v new zero digits. The zero list grows from n to about n + 2v.
4. The new value is cleared at the new depth. This gives a value of size about 2↑^(n+2v) (…), which is one step of
   the fast-growing function f_ω.

Then the same happens again with the new value, and the counter loses 14 in total. Every growth step takes the depth
from n to at least 2↑^n 4. The period map is n ↦ n' ≥ F(F(n)), so the whole run applies an f_ω-rate function
N = (6T − 19)/7 ≈ 0.86·2↑^37 3 times. In the fast-growing hierarchy this is the step from f_ω to f_(ω+1), since
f_(ω+1)(N) = f_ω applied N times.

**Why each growth step is "free".** The design can only work if unpacking the large parked value (step 3) costs
nothing that is in short supply. In n1 it doesn't. The unpack event turns a block D(1+3p) into 2p+1 zero digits and
carries the small "transit" value through unchanged, whatever the relative sizes. The Coq lemma `P2_B` holds for all
p and r with no hypothesis relating them. The earlier 10-state candidate M3 failed exactly here. Its unpack produced
a token 2R + 4 − (x−3)/2, so the small current value R had to pay for half of the parked value x. In the real run
x ≫ R, the payment fails, and M3 halts after its first period. M3 is therefore only f_ω-class (σ > 2↑^(4T+40) 4).
In n1 no small number ever pays for a large one.

**The end, and a lucky residue.** The counter starts at 6T − 19 and loses 14 per period. The final event needs
exactly 7 to be left, so 6T − 19 ≡ 7 (mod 14), which is the same as T ≡ 2 (mod 7). T is a tower of 2s with a huge
exponent, so T ≡ 2 (mod 7) does hold; Coq proves it (`T_mod7`). In other residue classes the countdown ends in a
different configuration that does not halt: such runs were followed for 100+ stages without a halt. At the end n1 does
one last unpack and clears the final value down to a D0 block. It then walks into a fixed 44-cell pattern left behind
in the far region and reads a 0 in state J: the halt.

**How big.** The final tape has about 3·2↑^(W+1)(2↑^n 5) ones, where W is the last depth. The machine-checked lower
bound is

    σ  >  G^N(33),   G(x) = 2↑^(x+1) 3,   N = (6·(2↑^37 3) − 19)/7,

i.e. G applied about 0.86·2↑^37 3 times. On paper this is roughly f_(ω+1)(0.86·2↑^37 3). For comparison, the published
champions (bbchallenge wiki "Champions", fetched 2026-10-08) are:

| n | published bound | relation to n1 | status of the comparison |
|---|---|---|---|
| 8 | > 2↑^37 3 > f_ω(36) (the record) | n1's phase 1 alone reaches this value | Coq (both) |
| 9 | > f_ω(2↑^13 3) > f_ω(f_ω(12)) | far smaller | on paper |
| **10** | **> f_ω(f_ω(25))** (Racheline 2024) | **n1 is larger** | **machine-checked**: `beats_champion` compares against the champion's own Coq-proved exact score |
| 11 | > f_ω(f_ω(10↑^4 4)) | n1's bound is larger | on paper |
| 12 | > f_ω(f_ω(f_ω(f_ω(f_4(2))))) | n1's bound is larger | on paper |
| 13 | > f_(ω+1)(2046) > g_64 | n1's bound is larger: f_ω-rate steps about 0.86·2↑^37 3 times versus 2046 times | on paper |
| 14 | > f_(ω+1)(f_ω(f_ω(f_ω(f_ω(f_7(3)))))) | larger than n1: its f_(ω+1) argument is far above 2↑^37 3 | on paper |

The BB(11)–BB(13) champions have published lower bounds only, with no proved upper bounds. So the paper comparisons
say only that n1's proved lower bound exceeds their published lower bounds. They do not say that n1 outscores those
machines. Since BB is increasing, the comparison does mean that, if accepted, n1 would give a better lower bound for
BB(11), BB(12) and BB(13) than the ones listed today. The comparison against the BB(10) champion is the only one
checked in Coq.

---

## 2. Notation and configuration families

### 2.1 Tokens and the B-form

- **Token.** D(m) = (10)^m 1, so D0 = `1`, D1 = `101`, D2 = `10101`, and so on. Juxtaposed tokens tokenize uniquely.
- **B-form.** `[t1, t2, …, tn | A]` is the configuration

      0^∞  D(t1) D(t2) … D(tn)  D0  D(A)  H>  0^∞

  The list is written **farthest token first**: tn is next to the head. A is the **accumulator**. The head is in
  state H on the blank cell right of the tape. `x^j` inside a list means j copies of token x; for example `1^35` is
  35 zero digits.
- **Digits.** D(3d+1) is the digit d, so `1` in a list is a zero digit and `4` is a one. Tokens of value < 3 that sit
  between nonzero digits (D0, D2) act as **blockers**: the clearing rules cannot borrow from them.
- **Value.** For an accumulator A ≡ 1 (mod 3), v = (A+8)/3 (Coq's g, with A = 3g − 8). Every accumulator from a
  clearing is ≡ 1 (mod 3) (Coq `r1_U`).
- **Far regions.** Some events move the counter part of the list to the left and leave a short gap. I write
  `Far + [list | A]` for "these bits, then the B-form".
  - `FarP(k, m)` = D2^(k+2) D5 D1^m D0 D0 D0 `00`, written by P2 and merged back by P3.
  - `FarE(k)` = D2^k followed by the fixed 44-cell tail `10110101010101010010000010111100100100100100`, written by
    the last unpack E.
- **Period start.** `Per(k, m, n, a)` = `[2^k, 5, 1^m, 0, 0, 2, 1^n | a]`. Here k counts the D2 run, m is the
  counter, n is the depth of the zero list, and a is the accumulator.

### 2.2 Other notations in the sources

All of them describe the same tape:

| source | form | conversion to the B-form above |
|---|---|---|
| Coq (`BB10_n1.v`) | `Bf L ts A`, ts nearest-first | reverse the list. Event lemmas are parameterized as in Coq (e.g. P1 input `1^(m+6)`), and I keep that. |
| verifier (`bb10_n1_verify.md`) | same B-form, farthest-first | Far(k,m) is labeled by P2's input m, so its counter drop shows up under P3. Its B is my B. |
| Ligocki / record family | B(a; d1, d2, …) | A = 3a + 1, v = a + 3. Ligocki's g_k(x) = 2↑^k(x+3) − 3 is v ↦ 2↑^k v. |
| BB(8) record Coq (`Kc ds a b`) | counter b | A = 6b + 4, v = 2b + 4. So the record's final b = B gives v = T. |
| bb8-ab (selector.md §6b) | `[list \| 1 \| R]` | = my `[list, 1 \| 2R+2]`. Their token "2R+3" is the transit token D(A+1) made by P2/P4 (section 3.4). Their k is my D2 count − 6 at the end, and their final n is my W − 1. |

---

## 3. Rules

All rules below are Coq lemmas of `proofs/BB10_n1.v`, each holding **for all values** of its parameters. I re-checked
each one with my own simulator, on literal instances run to the next B-form (counts in section 6.3).

### 3.1 The Ackermann list clearing (the record's R1/R2/R3)

These are the BB(7)/BB(8) champions' rules in B-form. They read no new state: of E, I and J they use only E1.

    R1   [L, t+3 | A]             ->  [L, t | 2A+8]                    (lower the digit next to the head; v -> 2v)
    R2   [L, t+3, 1^(k+1) | A]    ->  [L, t, A+3, 1^k | 4]             (borrow: the zero in front becomes A+3, i.e. the
                                                                         digit v-2; the accumulator resets to v = 4)

R1 and R2 compose into the clearing rule (Coq `CLR`, for A ≡ 1 mod 3 when n ≥ 1):

    CLR  [L, c+3d, 1^n | A]  ->  [L, c, 1^n | U_n^d(A)]        U_0(A) = 2A+8,  U_(j+1)(A) = U_j^((A-1)/3 + 1)(4)

Closed forms (Coq `U_closed`; the second is `iterU` of `BB10_n1_exact.v`):

    U_j(A) + 8 = 3 · 2↑^j ((A+8)/3)          i.e.  v -> 2↑^j v   per unit at depth j
    U_j^d(4) + 8 = 3 · 2↑^(j+1) (d+2)        (d units cleared at depth j, starting from a reset)

The record's R3, which borrows across several zeros, is R2 applied repeatedly inside CLR, so it needs no separate
rule here. The clearing stops when the token reaches c ∈ {0, 1, 2}. If c = 1 the token is a zero digit and the scan
continues. If c = 0 or 2 the token is a blocker, and one of the special events below fires.

**Worked example** (literal, my simulator). The list "digit 1 at depth 1" is [4, 1 | 4], with v = 4:

    step    0   [4, 1 | 4]       v = 4
    step  194   [1, 7 | 4]       R2: the 4 is borrowed to 1, the zero becomes 7 = digit 2 = v-2, reset
    step  606   [1, 4 | 16]      R1: v = 8
    step 2626   [1, 1 | 40]      R1: v = 16 = 2^4, as v -> 2↑^1 v predicts

### 3.2 Start-up and the record phase

    blank, state A   --6447 steps-->   [7, 1^35 | 4]          (digit 2 behind 35 zeros; Coq: `do 6447 step`)
    [7, 1^35 | 4]    --CLR-->          [1^36 | 3T-8]          (v: 4 -> 2↑^35 4 -> 2↑^35 2↑^35 4 = 2↑^37 3 = T)

The record's B is related by 3T − 8 = 6B + 4. Along the way the run passes [4^36 | 16] at step 48159, which is
Ligocki's B(5; [1]^36). Both landmarks re-checked literally. The first 48159 steps use only the 15 base slots A0–H1
without E0.

### 3.3 Stage 0: from the exhausted list to the first period

    H    [1^(n+1) | a]                 ->  [2, 1^(2a+4), 0, 1^n | 6]             (base states only: no E0 read)
    S0   [2, 1^(M+5), 0, 1^(n+2) | a]  ->  [2, 5, 1^M, 0, 0, 0, a+3, 1^n | 4]    (first E0 read; uses I0, I1, J1)

In the real run (Coq `reach_per`):

    [1^36 | 3T-8]
      -H->    [2, 1^(6T-12), 0, 1^35 | 6]                       (6T-12 = 12B+12: the counter is born)
      -S0->   [2, 5, 1^(6T-17), 0, 0, 0, 9, 1^33 | 4]
      -CLR->  [2, 5, 1^(6T-17), 0, 0, 0, 0, 1^33 | 3·2↑^34 5 - 8]      (the 9 = three units, cleared at depth 33)
      -P4 (q = 0, nothing parked)->  [2, 5, 1^(6T-19), 0, 0, r+2, 1^34 | 4],  r+1 = 3·2↑^34 5 - 8
      -CLR->  Per(1, 6T-19, 34, a0),   v0 = 2↑^35(2↑^34 5 - 1)

So the first period starts with k = 1, counter m0 = 6T − 19 = 12B + 5, depth n0 = 34 and value v0 > T.

### 3.4 The period events

DEP9 is R2 followed by CLR of the deposited 9 (three units), as a single lemma:

    DEP9 [L, t+3, 1^(d+1) | 6]  ->  [L, t, 0, 1^d | U_d^3(4)]        U_d^3(4) = 3·2↑^(d+1) 5 - 8

The four special events (exact Coq statements, farthest-first):

| event | before | after | what it does |
|---|---|---|---|
| **P1** | `[2^k, 5, 1^(m+6), 0, 0, 2, 1^n \| a]` | `[2^(k+2), 5, 1^m, 0, 0, 0, 1, a+3, 1^n \| 6]` | counter −6. Parks the value as token a+3 = P+3. |
| **P2** | `[2^k, 5, 1^(m+6), 0, 0, 0, 1, 1+3p, 0, 1^(w+1) \| r+1]` | `FarP(k, m) + [2, r+2, 1^(w+2p+2) \| 4]` | **growth**: the parked P = 1+3p becomes 2p+1 new zeros. The counter (−6) moves to the far region. The accumulator becomes the transit token r+2. |
| **P3** | `FarP(k, m) + [2, 2, 1^w \| a]` | `[2^(k+2), 5, 1^m, 0, 0, a+5, 1^w \| 6]` | merges the far region back. Parks the value as a+5 = Q+3. Base states only. |
| **P4** | `[2^k, 5, 1^(m+2), 0, 0, 3q, 0, 1^(w+1) \| r+1]` | `[2^k, 5, 1^m, 0, 0, r+2, 1^(w+2q+2) \| 4]` | **growth**: the parked Q = 3q becomes 2q+1 new zeros. Counter −2. Transit token r+2. |

P2 and P4 hold for **all** p, q, r. The unpack never compares the parked value with the transit, which is the
property M3 lacked. I checked both literally in both size orders, e.g. p = 1000 against r = 2 and p = 1 against
r = 999.

**The transit jump** (bb8-ab's "2R+3 jump"). After P2 or P4 the accumulator r+1 has become the token r+2 ≡ 2 (mod 3),
in front of the enlarged zero list. Here r = 3x (the accumulator is ≡ 1 mod 3), so CLR clears the token's x = r/3 units down to D2, each at the new depth.
This is where the new huge value is made.

**One period, composed** (Coq `PERIOD`; values written in v = (a+8)/3):

    Per(k, m+14, n, a)                                                         value v, depth n
      -P1->    [2^(k+2), 5, 1^(m+8), 0,0,0, 1, a+3, 1^n | 6]
      -DEP9->  [.., 1, a, 0, 1^(n-1) | ·]                                       v1 = 2↑^n 5
      -P2->    FarP(k+2, m+2) + [2, ·, 1^n2 | 4]                                n2 = n + 2v - 6
      -CLR->   FarP(k+2, m+2) + [2, 2, 1^n2 | ·]                                v2 = 2↑^(n2+1)(v1 - 1)
      -P3->    [2^(k+4), 5, 1^(m+2), 0,0, a'+5, 1^n2 | 6]
      -DEP9->  [.., 0,0, a'+2, 0, 1^(n2-1) | ·]                                 v3 = 2↑^n2 5
      -P4->    [2^(k+4), 5, 1^m, 0,0, ·, 1^n4 | 4]                              n4 = n2 + 2v2 - 4
      -CLR->   Per(k+4, m, n4, a'')                                             v' = 2↑^(n4+1)(v3 - 1)

Per period: **k += 4, m −= 14** (P1 −6, P2 −6, P4 −2), and the depth grows twice. Coq proves n4 ≥ F(F(n)) and keeps
the invariant a ≡ 1 (mod 3), a ≥ U_n(4). The exact map (n, v) ↦ (n4, v') is the `step` function of
`BB10_n1_exact.v`:

    n2 = n + 2v - 6
    n4 = n2 + 2·2↑^(n2+1)(2↑^n 5 - 1) - 4
    v' = 2↑^(n4+1)(2↑^n2 5 - 1)

This map is machine-checked (`PERIOD_U`, `step`, `score_closed`). I also re-derived it by hand from the event lemmas
above and the closed form of CLR.

### 3.5 The endgame and the halt

After JJ = (3T − 13)/7 periods the configuration is Per(4JJ+1, 7, n, a). The last period starts like the others:

    E     [2^(k+6), 5, 1, 0,0,0, 1, 1+3p, 0, 1^(w+1) | r+1]  ->  FarE(k) + [r+3, 1^(w+2p+2) | 4]
    HALT  FarE(k) + [0, 1^w | f]  ->  state J reads 0 (undefined): halt, with exactly 2w + f + 3k + 22 ones

The run (Coq `ENDGAME`, `HALT_B`, `HALT_exact`):

    Per(k+4, 7, n, a)
      -P1->    [2^(k+6), 5, 1, 0,0,0, 1, a+3, 1^n | 6]          (the counter is down to one digit)
      -DEP9->  [2^(k+6), 5, 1, 0,0,0, 1, a, 0, 1^(n-1) | ·]       v1 = 2↑^n 5
      -E->     FarE(k) + [r+3, 1^W | 4]                          W = n + 2v - 6 (the last unpack, E = P2 with m+6 = 1)
      -CLR->   FarE(k) + [0, 1^W | f]                            r+3 ≡ 0 (mod 3) clears to D0, not D2;
                                                                 f = 3·2↑^(W+1)(2↑^n 5) - 8
      -HALT->  J0

E differs from P2 in two ways. Because the counter is empty, the far region it writes is the fixed FarE tail, not a
re-mergeable FarP. And its transit token is r+3 instead of r+2, so the jump ends on a D0, which leads to the halt and
not to P3. The halting walk reads only the 44-cell tail, never the D2 run (bb8-ab: step count independent of k).
Literally the halt takes between 51 and 75,931 steps over my test grid. It halted for every tested (k, w, f), with
exactly 2w + f + 3k + 22 ones each time.

E0, I0, I1 and J1 are read only inside S0, P1, P2, P4, E and the halt walk. J0 is read only at the halt.

---

## 4. The full run from the blank tape

| # | configuration | via | notes |
|---|---|---|---|
| 0 | blank tape, state A | | |
| 1 | `[7, 1^35 \| 4]` | start-up | step 6447 (Coq) |
| – | `[4^36 \| 16]` | R1/R2 | step 48159 (literal); Ligocki's B(5; [1]^36) |
| 2 | `[1^36 \| 3T−8]` | CLR | the record's end: v = T = 2↑^37 3 |
| 3 | `[2, 1^(6T−12), 0, 1^35 \| 6]` | H | the counter is born |
| 4 | `[2, 5, 1^(6T−17), 0,0,0, 9, 1^33 \| 4]` | S0 | first E0 read |
| 5 | `Per(1, 6T−19, 34, a0)` | CLR, P4 (q = 0), CLR | v0 = 2↑^35(2↑^34 5 − 1) |
| 6 | `Per(1+4j, 6T−19−14j, n_j, a_j)` | j periods | n_(j+1) ≥ F(F(n_j)) |
| 7 | `Per(4JJ+1, 7, n, a)` | JJ = (3T−13)/7 periods | needs 6T − 19 ≡ 7 (mod 14), i.e. T ≡ 2 (mod 7) |
| 8 | `FarE(4JJ−3) + [0, 1^W \| f]` | P1, DEP9, E, CLR | W ≥ F^(2JJ+1)(34) |
| 9 | halt (J reads 0) | HALT | |

**Counts.** There are JJ = (3T − 13)/7 = (6B − 1)/7 ≈ 0.43T periods. The number of growth events (P2, P4 and E) is
N = 2JJ + 1 = (6T − 19)/7 = (12B + 5)/7 ≈ 0.86T. The counter goes 12B + 7 (stage 0) → 12B + 5 (after the first P4)
→ −14 per period → 7 → 1 (last P1). The D2 run ends at k = 4JJ − 3 inside FarE. The total step count has not been
computed. It is far larger than σ.

**Exact score (machine-checked, `BB10_n1_exact.v`, `score_closed`).** At the halt the tape holds exactly

    ones = 2W + f + 3k + 22                                    (Coq `score_exact`)
         = 2W + 3·2↑^(W+1)(2↑^n 5) + 12JJ + 5                  (Coq `score_closed`)

    where  JJ     = (3T − 13)/7,  T = 2↑^37 3
           (n, v) = step^JJ (34, 2↑^35(2↑^34 5 − 1))
           W      = n + 2v − 6
           step(n, v) = (n4, 2↑^(n4+1)(2↑^n2 5 − 1))
                  with n2 = n + 2v − 6  and  n4 = n2 + 2·2↑^(n2+1)(2↑^n 5 − 1) − 4

In words: each period applies `step` once, and that one call covers the period's two growths.
1. The first growth (P2) unpacks the parked value v into the zero list, so the depth goes from n to n2 = n + 2v − 6.
2. The value made by clearing at depth n2 is unpacked by P4, which takes the depth to n4.
3. The jump at depth n4 makes the next value, v' = 2↑^(n4+1)(2↑^n2 5 − 1).

The endgame is half a period. Its last unpack takes the depth to W = n + 2v − 6, and the final value is cleared to D0,
leaving f = 3·2↑^(W+1)(2↑^n 5) − 8. The run reaches the halt with k = 4JJ − 3 D2 tokens in the far region, so
3k + 22 + (−8) gives the constant 12JJ + 5.

Everything collapses to plain arrows because every clearing starts from the reset accumulator 4, and
(U_j)^d(4) = 3·2↑^(j+1)(d+2) − 8. This exact formula and the lower bound σ > G^N(33) (section 5) are both Coq theorems.
The bound is just the exact value with each growth step rounded down to n ↦ F(n). The standard score σ (the halting
transition writes a 1) is ones + 1. The ones are counted as follows. Each D2 gives 3.
The FarE tail gives 19. The block D0 D1^W D0 D(f) gives 2W + f + 3. Altogether this is 2W + f + 3k + 22, and the halt
walk does not change the count. The dominant term is the final accumulator, 3·2↑^(W+1)(2↑^n 5).

**A toy illustration** (verifier, hybrid run with B = 6 and fake clearing outputs in the real residue class). The zero
counts crossed by successive jumps were `33 34 33 380 379 888 887 1554 1553 2382 …`. Each pair-to-pair step is one
unpack of 2P/3 or 2Q/3. In the real run each of these steps is at least n ↦ F(n). No literal run can show even one
real period: the first DEP9 already clears at depth 33.

---

## 5. Size analysis

**Growth recurrence.**
- Each unpack adds 2p + 1 zeros, where the parked value is 1 + 3p ≥ U_n(4). With U_n(4) + 8 = 3F(n) this gives
  2p + 3 ≥ F(n) (Coq `growth`), so every growth event takes the depth from n to at least F(n) = 2↑^n 4.
- One period is two such events: n' ≥ F(F(n)) (Coq `PERIOD`).
- The endgame adds one more: W ≥ F(n).
- Starting from depth 34, the final depth is W ≥ F^(2JJ+1)(34) = F^N(34).

**Machine-checked bounds** (`proofs/BB10_n1_bound.v`; every theorem prints "Closed under the global context"):

    sigma_lower_bound : ones > iter ((6T-19)/7) (x |-> 2↑^(x+1) 3) 33
    dominates         : ones > (2↑^K)^x (x)   for all K, x <= F(F(F(34)))
    beats_M3_bound    : ones > 2↑^(4T+41) 2↑^(4T+39) 2↑^(4T+35) 5        (M3's proved lower bound; M3 has no upper bound)
    beats_lead        : ones > the exact score of the 10-state 0LJ0LC candidate
    beats_champion    : ones > the exact score of the BB(10) champion

**FGH reading (paper).** F(x) = 2↑^x 4 grows at the rate of f_ω under the usual correspondence 2↑^k x ≈ f_(k+1)(x).
So σ is about f_ω applied N ≈ 0.86·2↑^37 3 times, starting near 34. After two steps the start value is far above N,
which puts σ near f_(ω+1)(0.86·2↑^37 3), give or take a small shift in the argument. An f_ω-class machine applies f_ω a
fixed number of times; n1 applies it a number of times equal to the BB(8) record's value.

**Comparison with the related 10-state machines** (bb10_from_bb7 README standings, 2026-10-08). All of these are
single f_ω-scale applications:

| machine | σ (form) | status |
|---|---|---|
| **n1** | f_ω-rate step applied ≈ 0.86·2↑^37 3 times | Coq: halts, bound |
| c1 (bb8-ab) | 2↑^N' 5 < σ, N' = (76B + 141)/3 | strong evidence |
| M3 (`..._---0LJ_0LD0RA`) | σ > 2↑^(8B+56) 4 | strong evidence; f_(ω+1) claim withdrawn |
| M3J | 2↑^(z+4) 5 < σ < 2↑^(z+4) 6, z ≈ 2.4T | strong evidence |
| 0LJ0LC | σ = 2·(2↑^L 5) + 2L − 2, L = 4·(2↑^27 3) + 17 | Coq |
| BB(10) champion | > f_ω(f_ω(25)) | Coq (score and upper bound) |

---

## 6. Verification status, files and credit

### 6.1 What is machine-checked (Coq 8.20.1, busycoq)

| statement | file | status |
|---|---|---|
| `halt : halts tm c0` | `proofs/BB10_n1.v` (353 KB) | check.py PASS, no axioms. Lead's clean-room rebuild (`bb10_n1_coq/clean_room_build.txt`): ALL OK, 749 s |
| `score_exact`, `sigma_lower_bound`, `dominates`, `beats_M3_bound`, `beats_lead`, `beats_champion` | `proofs/BB10_n1_bound.v` | compiled, all Closed under the global context; in the clean-room rebuild (Closed x6) |
| `score_closed`, `score_closed_unfolded`, `score_value_gt` (the exact formula of §4) | `proofs/BB10_n1_exact.v` | machine-checked (bb8-ab's probe: Closed under the global context; not part of the 9-file clean-room rebuild). I also re-derived its formula by hand (§3.4). |
| every event lemma (H, S0, P1–P4, E, HALT, R1, R2, CLR, DEP9) and the chain (PERIOD, ENDGAME, reach_per) | inside `BB10_n1.v` | Coq |
| T ≡ 2 (mod 7), JJ = (3T−13)/7, Af = 3T − 8 | `BB10_n1.v` (arith part) | Coq |

Everything else is on paper: the FGH readings, the comparisons with the BB(11)–BB(14) champions, and the claim that
other residue classes do not halt.

### 6.2 Independent checks (before Coq)

- `investigations/bb10_n1_verify.md` (inv-bb10-fw1-verify). Independent simulator and rules. Rules checked on 72 random
  instances in both size orders. Whole hybrid chains for B = 6 and B = 20 halt. Literal stage 0 and endgame at
  B = 2526. Exactness of the transit jump. Cross-check of bb8-ab's far-region tail and ones formula.
- bb8-ab's Fable verifier, and the discovery notes in `halt_redirect/selector.md` §6b. These cover mini-follower
  chains (B ≡ 6 mod 14 halts; other classes don't), literal halt replays with far bits, and the far-region structure.
- `investigations/bb10_n1_coq.md`. The Coq report: it follows the verifier's chain event by event, and no correction
  was needed.

### 6.3 My own re-checks for this write-up

`investigations/bb10_n1_writeup_chk.py` is my own literal simulator and B-form parser, run at Idle priority for about
10 s. Results, 0 mismatches throughout:

| check | instances |
|---|---|
| start-up at step 6447 | `[7, 1^35 \| 4]` |
| step 48159 | `[4^36 \| 16]` |
| R1, R2 | 12 each |
| H | 30 |
| S0 | 45 |
| P1 | 15 |
| P2 | 24, both size orders (p up to 1000 with small r; r up to 999 with small p), far region exact |
| P3 | 12 |
| P4 | 18, both size orders |
| E | 12, far tail exact |
| HALT | 100: k ∈ {0,1,5,17}, w ∈ {0,1,2,7,30}, f ∈ {0,1,4,40,301}; all halt in J0 with exactly 2w + f + 3k + 22 ones |

Separately (not in the file), I recorded which E/I/J slots each event reads (§3.3–3.5) and the worked example of §3.1.

### 6.4 Credit

- **Found** by the parallel session **bb8-ab**, in its grow-and-count selector search over the G/H-sibling family
  (E0 redirected into new states I, J; `halt_redirect/selector.md` §6b). Every list-length filter missed n1. It was
  found by filtering the run histories on the size of the zero list that the jumps clear, after the lead's correction
  to judge growth by the cleared list.
- **Independently verified** by inv-bb10-fw1-verify (`bb10_n1_verify.md`) and by bb8-ab's Fable verifier.
- **Coq** by bb8-ab's inv-n1-coq (`bb10_n1_coq/`, `bb10_n1_coq.md`), building on our BB10_fw1 infrastructure (the
  B-form engine and the champion-rule lemmas). Clean-room rebuild by the lead.
- The underlying engine is the BB(7) champion's (Kropitz; analysis by Ligocki) and the BB(8) record's 35-digit start
  (Ketchersid 2026).
