# A 10-state machine at level f_(ω+1)

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_1RZ0LC

Below we call this machine **n1**. It halts from the blank tape, its exact score is proved in Coq, and the score
lies between two values of f_(ω+1). The current BB(10) champion has the published bound f_ω(f_ω(25)), at level ω of
the fast-growing hierarchy. n1 beats it and moves BB(10) to level ω+1. Written 2026-10-08.

|   | 0   | 1   |                                                    |
|---|-----|-----|----------------------------------------------------|
| A | 1RB | 0RA |                                                    |
| B | 1LC | 1LF |                                                    |
| C | 1RD | 0LB |                                                    |
| D | 1RA | 1LE |                                                    |
| E | 1LI | 0LC | E0 was the halting transition of the base machine  |
| F | 0RG | 1LD |                                                    |
| G | 1RH | 1LG |                                                    |
| H | 1LC | 0RG |                                                    |
| I | 0LJ | 0LI | new                                                |
| J | --- | 0LC | new; J0 is undefined and is the halt (`1RZ` in the string) |

**Where it comes from.** States A–H form an 8-state machine that we call the **base machine**. It agrees with the
BB(8) record `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_1LC0RH_1RG1LF` ([`../BB8/`](../BB8/)) on states A–E. It runs
the same digit-list computation as the record, which is the BB(7) champion's program with 36 digits. n1 keeps the
base machine, sends its halting transition E0 to a new state I, and adds the states I and J.

**Main facts.** Here T = 2↑^37 3, the value the BB(8) record computes, and F(x) = 2↑^x 4 = 2↑^(x+1) 3. "ones" is the
number of 1s on the tape when J reads 0. The standard score is σ = ones + 1, because the halting transition writes
a 1.

| | |
|---|---|
| Halts | **Yes**, machine-checked (Coq, no axioms). |
| Exact score | Machine-checked: ones = 2W + 3·2↑^(W+1)(2↑^n 5) + 12·JJ + 5, where JJ = (3T − 13)/7 and (n, W) come from an explicit recursion (section 4.4). |
| Lower bound | Machine-checked: ones > F^N(33), that is, F applied N = (6T − 19)/7 ≈ 0.86·T times to 33. |
| Level | Machine-checked, with the standard fast-growing hierarchy: f_(ω+1)(JJ − 2) < ones < f_(ω+1)(6T). |
| Graham's number | Machine-checked: ones > Graham's number. |
| BB(10) champion | **Beaten**, machine-checked against the champion's own Coq-proved exact score. |

---

## 1. How it works

### 1.1 Reading the tape

The notation follows Ligocki's analysis of the BB(7) champion (bbchallenge wiki page for
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF`).

- **Tokens.** The tape is a string of blocks D(t) = (10)^t 1. So D0 = `1`, D1 = `101`, D2 = `10101`, and so on. A
  string of blocks splits into tokens in only one way.
- **Configurations.** `[t_1, t_2, …, t_k | A]` means the tape

      0^∞  D(t_1) D(t_2) … D(t_k)  D0  D(A)  H>  0^∞

  The tokens are listed left to right, as on the tape, so t_k is next to the head. A is the **accumulator**. The
  D0 just left of it is part of the notation and is not listed. The head is in state H on the blank cell right of
  D(A). Inside a list, x^j means j copies of the token x.
- **Digits and zeros.** A token 3d + 1 is the digit d. In particular the token 1 (that is, D1) is a **zero**, and
  `1^n` means n zeros.
- **Units and blockers.** A token 3d + c with c ∈ {0, 1, 2} holds d **units**. Clearing removes units one at a time.
  When a token has no units left it becomes c. If c = 1 it is a zero. If c = 0 or c = 2 it is a **blocker**: the
  clearing rules cannot borrow from D0 or D2.
- **Depth.** The depth of a token is the number of zeros between it and the accumulator. In `[…, t, 1^j | A]` the
  token t has depth j.
- **Value.** The value of an accumulator A ≡ 1 (mod 3) is v = (A + 8)/3. A reset accumulator A = 4 has v = 4.
- **Arrows.** 2↑^0 x = 2x, 2↑^1 x = 2^x, and 2↑^(k+1) x applies 2↑^k x times, starting from 1. Two identities are used
  often: 2↑^k 2 = 4, and 2↑^(k+1) 3 = 2↑^k 4.

In Ligocki's notation, B(a; d_1, …, d_k) = `[3d_k+1, …, 3d_1+1 | 3a+1]` and v = a + 3. His g_j(x) = 2↑^j(x+3) − 3
(with the BB(8) record's constants) is the map v ↦ 2↑^j v below.

**Example.** At step 6447 n1 is in the configuration `[7, 1^35 | 4]`: one digit 2, then 35 zeros, then the
accumulator 4 (v = 4). On the tape this is D7 (D1)^35 D0 D4, that is,

    101010101010101 (101)^35 1 101010101 H>

In Ligocki's notation it is B(1; [0]*35, 2), the start of the BB(8) record's main phase.

### 1.2 The engine

n1 uses the clearing rules of the BB(7) champion and the BB(8) record:

> **Clearing one unit of a token at depth j changes the value v into 2↑^j v.**

At depth 0 this doubles v. At depth 1 it gives 2^v, and at depth 2 a tower of v twos. Clearing always works on the
nearest token that is not a zero. If that token is a blocker, no clearing rule applies and the list is
**exhausted**. In the BB(8) record an exhausted list leads to the halt. In n1 it starts one of the special events
of section 2.

### 1.3 Phase 1: the BB(8) record's computation

From the blank tape, n1 reaches `[7, 1^35 | 4]` after 6447 steps. It then clears the two units of the 7 at depth
35:

    v = 4  →  2↑^35 4  →  2↑^35 (2↑^35 4) = 2↑^36 4 = 2↑^37 3 = T

The result is `[1^36 | 3T − 8]`: 36 zeros and the value v = T. These are the record's own configurations. The BB(8)
record halts here, and its final sweep writes about 12T ones. In simulation the rules used up to this point never
read E0 (section 1.8), so here n1 behaves exactly like the base machine.

### 1.4 Phase 2: T becomes a countdown

The list is exhausted. A walk to the left (event H) writes 2A + 4 = 6T − 12 new zeros at the far left. Then S0 (the
first read of E0) tidies the left end. A clearing, an event P4 with nothing parked yet, and another clearing then
give the first **period start**:

    [2, 5, 1^(6T−19), 0, 0, 2, 1^34 | A]

Reading from the left:

- the first 2 is debris: a run of D2 tokens, one here, with 4 more added each period;
- the 5 is a marker;
- `1^m` is the **counter**, here m = 6T − 19 zeros;
- the D0 D0 pair is a wall;
- the next D2 is a blocker;
- `1^n` is the **active list**, here n = 34 zeros;
- the accumulator holds a huge value, v > T.

The clearing rules only ever act on the active list. Between the active list and the counter there is always a
blocker (a D2, a D0, or the D0 D0 wall), so the clearing never uses the counter's zeros as digits. Only the special
events touch the counter, and each removes a fixed number of zeros: 6 + 6 + 2 = 14 per period.

### 1.5 Phase 3: the periods

At a period start the active list is exhausted: it holds only zeros, and its far end is the blocker D2. A period
runs the same four-step cycle twice.

1. **Park.** The accumulator moves into the list, as a token just beyond the zeros (event P1, or P3 the second
   time). Its value v is now stored. The accumulator resets to 6.
2. **Fresh small value.** R2 borrows one unit from the parked token and writes the 6 into the zero next to it, as
   a token 9 (three units, at depth n − 1). Clearing those units gives the fresh value v₁ = 2↑^n 5. The 9 ends as
   a D0, so the list is exhausted again.
3. **Unpack.** Event P2 (or P4) turns the parked token, which holds about v units, into about **2v new zeros** of the
   active list. The accumulator, which holds v₁, becomes a token on the far side of the new zeros: the **transit
   token**. The accumulator resets to 4.
4. **Jump.** Clearing the transit token at the new depth n' ≈ n + 2v gives a new value of about 2↑^(n'+1) v₁. The
   transit token ends as a D2 blocker, so the list is exhausted again and the next step is a park.

Each half-period therefore takes the depth from n to about n + 2v, where v is already at least 2↑^n 4. So the depth
goes from n to at least F(n) = 2↑^n 4 (Coq lemma `growth`), and one period goes from n to at least F(F(n)). F grows
at the rate of f_ω: 2↑^n 4 is roughly f_(n+1)(4), and Coq proves f_ω(x) ≤ F(F(x)) for x ≥ 3.

The unpack is free. P2 and P4 hold for every parked value and every transit value, with no condition relating the
two. The small current value never has to pay for the large parked one.

### 1.6 Phase 4: the end

The counter starts at 6T − 19 and loses 14 per period. When a period starts with the counter at 7, P1 takes 6 and
leaves 1. That is too few for P2, so the final unpack is a different event, E. It writes a fixed 44-cell pattern at
the far left. Its transit token is ≡ 0 (mod 3), so it clears down to a D0 instead of a D2. The machine then walks
left into the fixed pattern and reaches state J reading 0: the halt.

The counter reaches exactly 7 only if 6T − 19 ≡ 7 (mod 14), that is, T ≡ 2 (mod 7). Coq proves T ≡ 2 (mod 7)
(`T_mod7`). So there are JJ = (3T − 13)/7 ≈ 0.43·T full periods and then the endgame, which is half a period. In all
there are N = 2·JJ + 1 = (6T − 19)/7 unpacks, not counting the empty P4 of the set-up.

### 1.7 Why the level is ω+1

f_(ω+1)(x) is f_ω applied x times to x. n1 makes N ≈ 0.86·T steps of f_ω size, starting from depth 34. So its score
is about f_(ω+1)(T), up to a small change in the argument. Coq proves

    f_(ω+1)((3T − 13)/7 − 2)  <  ones  <  f_(ω+1)(6T).

A machine at level ω, such as the BB(10) champion, applies f_ω a fixed number of times. n1 applies it a number of
times equal to the BB(8) record's value.

### 1.8 What the new states cost

Compared with the base machine, n1 changes one transition (E0) and adds two states (I and J). In simulation on
small instances (section 6.3), R1, R2, H and P3 read only transitions of the base machine. E0, I0, I1 and J1 are
read only inside S0, P1, P2, P4, E and the final walk, and J0 is read only at the halt. So the countdown, the
parking and the unpacking all come from this one rewired transition and two new states.

---

## 2. The rules

Every rule in this section is a lemma of [`verify/multifile/BB10_n1.v`](verify/multifile/BB10_n1.v). Each holds for
all values of its parameters. Coq lists tokens nearest-first. Here they are written left to right, as in section 1.1.
X stands for any tokens further left.

### 2.1 Clearing

    R1    [X, t+3 | A]              →  [X, t | 2A + 8]
    R2    [X, t+3, 1^(k+1) | A]     →  [X, t, A+3, 1^k | 4]

R1 lowers the token next to the accumulator and doubles v. R2 borrows one unit from the nearest nonzero token; the
zero next to it becomes A + 3 (the digit v − 2), and the accumulator resets to 4. Composed, they give `CLR`
(for n = 0, or for A ≡ 1 mod 3):

    CLR   [X, c + 3d, 1^n | A]      →  [X, c, 1^n | U_n^d(A)]

where U_n^d means U_n applied d times, U_0(A) = 2A + 8, and U_(j+1)(A) = U_j applied (A−1)/3 + 1 times to 4. The
closed forms (`U_closed` in `BB10_n1.v`, `iterU` in `BB10_n1_exact.v`) are

    U_j(A) + 8   = 3 · 2↑^j ((A + 8)/3)        one unit at depth j:  v ↦ 2↑^j v   (A ≡ 1 mod 3)
    U_j^d(4) + 8 = 3 · 2↑^(j+1) (d + 2)        d units at depth j from a reset:  v = 2↑^(j+1)(d + 2)

In the run every accumulator that a clearing produces is ≡ 1 (mod 3) (Coq `r1_U`). The only other accumulator
value is the 6 left by H, P1 and P3. After H it is used by S0. After P1 and P3 it is used at once by DEP9, which is
R2 followed by CLR:

    DEP9  [X, t+3, 1^(d+1) | 6]     →  [X, t, 0, 1^d | U_d^3(4)]          U_d^3(4) = 3·2↑^(d+1) 5 − 8

### 2.2 The special events

Two far-left patterns appear:

- FarP(k, m) = D2^(k+2) D5 D1^m D0 D0 D0 `00`. P2 writes it and P3 merges it back.
- FarE(k) = D2^k followed by the fixed 44 cells `10110101010101010010000010111100100100100100`. E writes it.

`FarP(k, m) + [list | A]` means the far pattern followed directly by the configuration `[list | A]`.

| event | from | to | what it does |
|---|---|---|---|
| H | `[1^(n+1) \| A]` | `[2, 1^(2A+4), 0, 1^n \| 6]` | the exhausted list writes 2A + 4 new zeros at the far left |
| S0 | `[2, 1^(M+5), 0, 1^(n+2) \| A]` | `[2, 5, 1^M, 0, 0, 0, A+3, 1^n \| 4]` | sets up the marker and the wall; first read of E0 |
| P1 | `[2^k, 5, 1^(m+6), 0, 0, 2, 1^n \| A]` | `[2^(k+2), 5, 1^m, 0, 0, 0, 1, A+3, 1^n \| 6]` | parks v as the token A + 3; counter −6 |
| P2 | `[2^k, 5, 1^(m+6), 0, 0, 0, 1, 1+3p, 0, 1^(w+1) \| A]` | `FarP(k, m) + [2, A+1, 1^(w+2p+2) \| 4]` | unpack: the parked 1 + 3p gives 2p + 1 new zeros; A becomes the transit token A + 1; counter −6 |
| P3 | `FarP(k, m) + [2, 2, 1^w \| A]` | `[2^(k+2), 5, 1^m, 0, 0, A+5, 1^w \| 6]` | merges the far pattern back; parks v as A + 5 |
| P4 | `[2^k, 5, 1^(m+2), 0, 0, 3q, 0, 1^(w+1) \| A]` | `[2^k, 5, 1^m, 0, 0, A+1, 1^(w+2q+2) \| 4]` | unpack: the parked 3q gives 2q + 1 new zeros; transit token A + 1; counter −2 |
| E | `[2^(k+6), 5, 1, 0, 0, 0, 1, 1+3p, 0, 1^(w+1) \| A]` | `FarE(k) + [A+2, 1^(w+2p+2) \| 4]` | the last unpack (P2 with one counter zero left); transit token A + 2 |
| HALT | `FarE(k) + [0, 1^w \| f]` | J reads 0 | halts with exactly 2w + f + 3k + 22 ones |

In Coq these are `H_B`, `S0_B`, `P1_B`, `P2_B`, `P3_B`, `P4_B`, `E_B` and `HALT_B` (the ones count is `HALT_exact` and
`ones_c_halt` in `BB10_n1_bound.v`). Coq writes the accumulator of P2, P4 and E as r + 1.

**The transit token.** In the run, A ≡ 1 (mod 3), so the transit token A + 1 is 2 + 3x with x = (A − 1)/3 = v − 3.
CLR clears its x units at the new depth and stops at the D2. E's token A + 2 = 3(v − 2) clears down to D0 instead.

**Worked example (literal simulation).** Take P4 with k = 1, m = 0, q = 2, w = 0 and A = 4:

    [2, 5, 1, 1, 0, 0, 6, 0, 1 | 4]
       = 10101 10101010101 101 101 1 1 1010101010101 1 101 1 101010101 H>

After 534 steps the machine is in

    [2, 5, 0, 0, 5, 1^6 | 4]
       = 10101 10101010101 1 1 10101010101 (101)^6 1 101010101 H>

The parked token 6 (q = 2) has become 2q + 1 = 5 new zeros, so the active list grew from 1 zero to 6. The
accumulator 4 has become the transit token 5, which holds one unit. The counter lost its 2 zeros. With the parked
token 30 (q = 10) instead, the same event gives 21 new zeros (1462 steps).

---

## 3. One period

Write v = (A + 8)/3 for the value at the period start, and

    Per(k, m, n, A) = [2^k, 5, 1^m, 0, 0, 2, 1^n | A]

(debris k, counter m, depth n, accumulator A). Coq's `PERIOD` composes the events. Here A = 1 + 3p, so p = v − 3:

    Per(k, m+14, n, A)                                                   value v, depth n
      P1    →  [2^(k+2), 5, 1^(m+8), 0,0,0, 1, A+3, 1^n | 6]             park v
      DEP9  →  [2^(k+2), 5, 1^(m+8), 0,0,0, 1, A, 0, 1^(n−1) | A1]       v1 = 2↑^n 5
      P2    →  FarP(k+2, m+2) + [2, A1+1, 1^n2 | 4]                      n2 = n + 2v − 6
      CLR   →  FarP(k+2, m+2) + [2, 2, 1^n2 | A2]                        v2 = 2↑^(n2+1)(v1 − 1)
      P3    →  [2^(k+4), 5, 1^(m+2), 0,0, A2+5, 1^n2 | 6]                park v2
      DEP9  →  [2^(k+4), 5, 1^(m+2), 0,0, A2+2, 0, 1^(n2−1) | A3]        v3 = 2↑^n2 5
      P4    →  [2^(k+4), 5, 1^m, 0,0, A3+1, 1^n4 | 4]                    n4 = n2 + 2v2 − 4
      CLR   →  Per(k+4, m, n4, A')                                       v' = 2↑^(n4+1)(v3 − 1)

The values follow from the closed form of CLR, because every clearing here starts from the reset accumulator 4
(DEP9 clears 3 units; the transit tokens hold v1 − 3 and v3 − 3 units). Per period the debris grows by 4 and the
counter falls by 14. `PERIOD` keeps the invariant n ≥ 3, A ≡ 1 (mod 3), v ≥ F(n), and proves n4 ≥ F(F(n)).

The exact period map is the function `step` of [`BB10_n1_exact.v`](verify/multifile/BB10_n1_exact.v):

    step(n, v) = (n4, 2↑^(n4+1)(2↑^n2 5 − 1))
        where  n2 = n + 2v − 6,   n4 = n2 + 2·2↑^(n2+1)(2↑^n 5 − 1) − 4

No literal simulation can show a whole period, because even the first DEP9 of the real run clears at depth 33.

---

## 4. The run and the score

### 4.1 Start and the BB(8) phase

    blank tape, state A   --6447 steps-->  [7, 1^35 | 4]           (Coq: init_reach)
    [7, 1^35 | 4]         --CLR-->         [1^36 | 3T − 8]         (v: 4 → 2↑^35 4 → 2↑^37 3 = T)

On the way the run passes `[4^36 | 16]` at step 48159. In Ligocki's notation this is B(5; [1]*36). The record
reaches the same two configurations at steps 6413 and 47897.

### 4.2 Building the countdown

This is Coq's `reach_per`:

    [1^36 | 3T−8]
      H     →  [2, 1^(6T−12), 0, 1^35 | 6]                       the counter is written
      S0    →  [2, 5, 1^(6T−17), 0, 0, 0, 9, 1^33 | 4]
      CLR   →  [2, 5, 1^(6T−17), 0, 0, 0, 0, 1^33 | A]           A = 3·2↑^34 5 − 8 (three units at depth 33)
      P4    →  [2, 5, 1^(6T−19), 0, 0, A+1, 1^34 | 4]            q = 0: nothing parked yet
      CLR   →  Per(1, 6T−19, 34, A0)                             v0 = 2↑^35(2↑^34 5 − 1) > T

### 4.3 The whole run

| | configuration | how | proved in Coq |
|---|---|---|---|
| 0 | blank tape, state A | | |
| 1 | `[7, 1^35 \| 4]` | 6447 steps | `init_reach` |
| 2 | `[1^36 \| 3T−8]` | CLR | inside `reach_per` |
| 3 | `Per(1, 6T−19, 34, A0)` | H, S0, CLR, P4, CLR | `reach_per` |
| 4 | `Per(1+4j, 6T−19−14j, n_j, A_j)` | j periods, with n_(j+1) ≥ F(F(n_j)) | `PERIOD`, `PERIODS` |
| 5 | `Per(4·JJ+1, 7, n, A)` | JJ = (3T−13)/7 periods; uses T ≡ 2 (mod 7) | `JJ_eq`, `T_mod7` |
| 6 | `FarE(4·JJ−3) + [0, 1^W \| f]` | P1, DEP9, E, CLR | `ENDGAME` |
| 7 | J reads 0 | the halting walk | `HALT_B`, `HALT_exact` |

The endgame, from row 5 (k = 4·JJ − 3):

    Per(k+4, 7, n, A)
      P1    →  [2^(k+6), 5, 1, 0,0,0, 1, A+3, 1^n | 6]              one counter zero left
      DEP9  →  [2^(k+6), 5, 1, 0,0,0, 1, A, 0, 1^(n−1) | A1]        v1 = 2↑^n 5
      E     →  FarE(k) + [A1+2, 1^W | 4]                            W = n + 2v − 6
      CLR   →  FarE(k) + [0, 1^W | f]                               f = 3·2↑^(W+1)(2↑^n 5) − 8
      HALT  →  J reads 0

The halting walk reads only the 44-cell pattern, never the D2 debris. In simulation its length does not depend on k.
The total number of steps has not been computed. It is far larger than the score.

### 4.4 The exact score

At the halt the tape holds exactly

    ones = 2W + f + 3k + 22                                         (Coq: score_exact)
         = 2W + 3·2↑^(W+1)(2↑^n 5) + 12·JJ + 5                      (Coq: score_closed_unfolded)

    where  T      = 2↑^37 3
           JJ     = (3T − 13)/7
           (n, v) = step applied JJ times to (34, 2↑^35(2↑^34 5 − 1))
           W      = n + 2v − 6

The count is easy to read off the final tape. A token D(t) has t + 1 ones, so the k = 4·JJ − 3 debris tokens D2 give
3k. The fixed pattern gives 19. The tokens D0 D1^W D0 D(f) give 2W + f + 3. The halting walk does not change the
count. The standard score is σ = ones + 1.

---

## 5. Size

### 5.1 Machine-checked bounds

From [`BB10_n1_bound.v`](verify/multifile/BB10_n1_bound.v):

- **Growth.** Each unpack takes the depth from n to at least F(n) = 2↑^n 4. There are N = 2·JJ + 1 = (6T − 19)/7
  unpacks, so W ≥ F^(2JJ+1)(34), that is, F applied 2·JJ + 1 times to 34 (`score_exact`).
- `sigma_lower_bound`: ones > F^N(33). Coq states it with G(x) = 2↑^(x+1) 3, which equals F(x).
- `dominates`: ones > (2↑^K)^x (x), the map 2↑^K applied x times to x, for all K, x ≤ F(F(F(34))).

From [`BB10_n1_fgh.v`](verify/multifile/BB10_n1_fgh.v), with the standard fast-growing hierarchy
(f_0(x) = x + 1, f_(k+1)(x) = f_k applied x times to x, f_ω(x) = f_x(x), f_(ω+1)(x) = f_ω applied x times to x)
and Graham's number g_64 (g_0 = 4, g_(k+1) = 3↑^(g_k) 3):

- `fgh_level`: f_(ω+1)((3T−13)/7 − 2) < ones < f_(ω+1)(6T). So the level is ω+1, not ω and not ω+2.
- `fgh_lower_64`: ones > f_(ω+1)(64).
- `graham_lt_f_omega1_64`: g_64 < f_(ω+1)(64). Together with the previous line, `beats_graham`: ones > g_64.

### 5.2 Comparison with the published champions

The bounds are from the bbchallenge wiki "Champions" page, as of 2026-10-08.

| n | champion | published lower bound | compared with n1 | status |
|---|---|---|---|---|
| 8 | Ketchersid 2026 (the BB(8) record) | 2↑^37 3 > f_ω(36) | n1's first phase computes the same value T | Coq, for both machines |
| 9 | Ketchersid 2026 | f_ω(2↑^13 3) > f_ω(f_ω(12)) | far below n1 | on paper |
| **10** | **Racheline 2024** | **f_ω(f_ω(25))** | **n1 is larger** | **Coq** (`beats_champion`, against the champion's Coq-proved exact score) |
| 11 | Jacobzheng 2026 | f_ω(f_ω(10↑^4 4)) | n1's lower bound is larger | on paper |
| 12 | Racheline 2024 | f_ω(f_ω(f_ω(f_ω(2↑↑↑4 − 3)))) > f_ω(f_ω(f_ω(f_ω(f_4(2))))) | n1's lower bound is larger | on paper |
| 13 | 50_ft_lock 2026 | f_(ω+1)(2046) > g_64 | n1's lower bound is larger (argument ≈ 0.43·T instead of 2046) | on paper |
| 14 | Jacobzheng 2026 | f_(ω+1)(f_ω(f_ω(f_ω(f_ω(f_7(3)))))) | above n1's upper bound f_(ω+1)(6T) | on paper |

The paper comparisons combine `fgh_level` with monotonicity and assume that the wiki uses the same standard
definitions. For example, for x ≥ 4, f_(ω+1)(x) ≥ f_ω(f_ω(f_ω(f_ω(x)))), and JJ − 2 is far above 2↑↑↑4.

The BB(11)–BB(13) champions have published lower bounds only. So the paper comparisons show only that n1's proved
lower bound exceeds their published lower bounds, not that n1 outscores those machines. Because BB is increasing,
n1 would still raise the known lower bounds for BB(11), BB(12) and BB(13), if accepted. The comparison with the
BB(10) champion is the only one checked in Coq.

The Coq development also proves (`beats_lead`) that n1 beats an unpublished 10-state machine of the same family,
whose proofs are the `BB10_lead_*` files in `verify/multifile/`.

---

## 6. Verification

### 6.1 What Coq proves

The development is in [`verify/multifile/`](verify/multifile/). It uses Coq 8.20.1 on top of
[busycoq](https://github.com/meithecatte/busycoq) (commit `bd2e36f`). See [`verify/README.md`](verify/README.md).

| statement | Coq name | file |
|---|---|---|
| n1 halts from the blank tape | `halt` | `BB10_n1.v` |
| every rule of sections 2–4, for all parameters; T ≡ 2 (mod 7); JJ = (3T−13)/7 | `R1`, `R2`, `CLR`, `DEP9`, `H_B`, `S0_B`, `P1_B`–`P4_B`, `E_B`, `HALT_B`, `PERIOD`, `ENDGAME`, `reach_per`, `T_mod7` | `BB10_n1.v` |
| exact ones count 2w + f + 3k + 22, with w ≥ F^(2JJ+1)(34) | `score_exact` | `BB10_n1_bound.v` |
| the closed formula of section 4.4 | `score_closed_unfolded`, `score_value_gt` | `BB10_n1_exact.v` |
| lower bounds | `sigma_lower_bound`, `dominates` | `BB10_n1_bound.v` |
| n1 beats the BB(10) champion | `beats_champion` | `BB10_n1_bound.v` (with `BB10_champion_*.v`) |
| n1 beats an unpublished 10-state machine | `beats_lead` | `BB10_n1_bound.v` (with `BB10_lead_*.v`) |
| level ω+1 | `fgh_level`, `fgh_lower_64` | `BB10_n1_fgh.v` |
| more than Graham's number | `graham_lt_f_omega1_64`, `beats_graham` | `BB10_n1_fgh.v` |

`compile_clean.sh` rebuilds everything from scratch, in about 20 minutes, and then runs `probe.v`. The probe does
three things:

- it checks all 20 entries of the transition table against the machine string, by conversion;
- it prints the definitions the statements use (`arrow`, `F`, `iter`, `JJ`, `ones`, `step`, `fgh`, `Graham`, …);
- it runs `Print Assumptions` on the twelve main theorems. All twelve report "Closed under the global context".

The logs are `compile_clean.log` and `probe.log`.

**Single file.** [`verify/BB10_n1_selfcontained.v`](verify/BB10_n1_selfcontained.v) is the same proof in one file
that needs only the Coq standard library. `coqc` checks it in about 13 minutes and ends with 28 `Print Assumptions`,
all closed. Its probe makes 61 conversion checks of the transition tables and runs 18 more `Print Assumptions`, all
closed.

### 6.2 Not machine-checked

- The comparisons with the BB(11)–BB(14) champions (section 5.2). They are on paper.
- The intuitive statements of section 1, for example "f_ω-sized step". The precise versions are the Coq theorems
  above.
- The step counts of individual events, which transitions each event reads (section 1.8), and the fact that the
  halting walk's length does not depend on k. These come from simulation.

### 6.3 Literal simulation

[`tools/bb10_n1_writeup_chk.py`](tools/bb10_n1_writeup_chk.py) is a separate cell-by-cell simulator (Python 3,
standard library only, about 10 s). It shares no code with the Coq proof. It checks each rule on concrete
instances, run to the next configuration of the form of section 1.1. 0 mismatches:

| check | instances |
|---|---|
| step 6447 | `[7, 1^35 \| 4]` |
| step 48159 | `[4^36 \| 16]` |
| R1, R2 | 12 each |
| H | 30 |
| S0 | 45 |
| P1 | 15 |
| P2 | 24, in both size orders (p up to 1000 with small A; A up to 1000 with small p); far pattern exact |
| P3 | 12 |
| P4 | 18, in both size orders |
| E | 12; far pattern exact |
| HALT | 100: k ∈ {0, 1, 5, 17}, w ∈ {0, 1, 2, 7, 30}, f ∈ {0, 1, 4, 40, 301}; every case halts in J0 with exactly 2w + f + 3k + 22 ones, after 51 to 75,931 steps |

Before the Coq proof, two other independent simulators checked the same rules. They also made "hybrid" runs, in
which every special event is simulated literally but each long clearing is replaced by a small stand-in value of the
right residue. With the counter in the real residue class, these runs reach the halt in J0.

---

## 7. Discovery and credit

- **Found** on 2026-10-08 by a computer search over 10-state machines that keep the base machine (states A–H) and
  send its halting transition E0 into two new states. Run histories were filtered by the length of the list that
  each clearing actually crosses. A filter on total tape size missed n1.
- **Checked** first by independent literal simulations (section 6.3), then **proved** in Coq on top of busycoq.
- **Built on** the BB(7) champion (Kropitz 2025, analysis by Ligocki) and the BB(8) record (Ketchersid 2026,
  [`../BB8/`](../BB8/)).
