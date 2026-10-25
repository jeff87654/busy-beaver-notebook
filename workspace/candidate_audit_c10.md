# Universal C-configuration rules for C10

Machine:

`1RB1LA_0LA0RC_1RA1LD_0LE1RZ_1LC1LF_1RG0LE_1LD1RH_0RE0RG`

All words below have zero tape outside them. Configurations differing by
translation are equivalent. A right-pointing state marker scans the cell
immediately to its right. In P, the head position is stated explicitly.

Define:

- C(a,b): `1111 (01)^a 0 1^b 01 H> 0...`, for a >= 0 and odd b >= 1.
- E(n): `1^n 01 H> 0...`.
- P(u,k,v): tape `1111 (01)^u (01)^k 1 (01)^v 1`, with E scanning
  the last 1 of the prefix `1111 (01)^u`.
- R(k,v): `1111 H> (01)^k 1 (01)^v 1 0...`.

The boundaries in P distinguish its two adjacent runs of `(01)`; they
specify the head position, even though the unmarked tape word merges them.

## Elementary transition sequences

These facts follow directly from the displayed transition table:

1. H scanning a pair `01` changes it to `11`, moves two cells right,
   and returns to H in four transitions: H0, E1, F0, G1.
2. E scanning the rightmost cell of `1^(2r)` converts that block to
   `(01)^r`, moves to the cell immediately left of it, and remains E
   after 2r transitions: repeat E1, F1.
3. E scanning the 1 in a left-hand pair `01` changes that pair to `11`
   and reaches H immediately to its right in three transitions:
   E1, F0, G1.
4. H scanning `10` changes it to `01` and reaches E immediately to its
   left in three transitions: H1, G0, D0. The D0 read is guaranteed by
   H1 having just written zero there.
5. H scanning `11` changes it to `01` and reaches H immediately to
   its right in two transitions: H1, G1.
6. E scanning a blank immediately left of the displayed word, with
   blank tape farther left, executes E0, C0, A1, A1 in four transitions.
   It reaches A on a blank with two newly written ones to its right.
7. Starting from `...00 A> 0 11 W`, the sequence
   A0, B1, C1, D0, E1, F0, G1, H0, E1, F0, G1
   reaches `...0 1111 H> W` in eleven transitions. The sequence touches
   only the displayed zero and two ones, plus the blank immediately
   to their left; W is arbitrary and is not read.

Repeating items 1 and 2 is justified by induction on the number of pairs:
the state and the next unread pair have the same form after every copy.
No transition in these sequences halts.

## Entry from C

For every C(a,b), the first eleven transitions reach F on the last 1 of
the original `1^b` block. The tape is now
`1111 (01)^a 0 1^(b+1) 011`.

The next b transitions alternate F1 and E1 while sweeping left through
the original odd-length block. E then scans its zero separator. Three
more transitions are E0, C1 and either D0 or D1:

- If a = 0, D scans a prefix 1 and D1 halts. Total: b+14 transitions.
  The final number of ones is `(b+15)/2`.
- If a > 0, D scans the zero of the last `(01)` pair. D0 reaches
  P(a-1, 1, (b+3)/2). Total: b+14 transitions.

## Interior P loop

For u >= 1 and v >= 1,

`P(u,k,v) -> P(u-1,k+2,v-1)` in `6k+8` transitions.

Proof: item 3 turns the final left pair into two ones (3 transitions).
Item 1 converts the k pairs to its right into another 2k ones (4k).
The next symbols are `10`, so item 4 bounces left (3), leaving the
right suffix `(01) 1 (01)^(v-1) 1`. Item 2 sweeps the `2k+2` newly
consecutive ones to its left (2k+2), converting them into `k+1` pairs.
Those pairs followed by the bounce's pair give the new k+2 pairs.

## The v = 0 boundary, including u = 1

For u >= 1, item 3, then k applications of item 1, then item 5 give

`P(u,k,0) -> 1111 (01)^(u-1) 1^(2k+2) 01 H>`

in `4k+5` transitions. Consequently:

- u >= 2 gives C(u-2, 2k+3).
- u = 1 gives E(2k+6).

The second case is essential: it covers `a = (b+7)/2` in the original
C rule and must not be treated as a negative-a C configuration.

## The u = 0 boundary

First,

`P(0,k,v) -> R(k+2,v)` in 19 transitions.

Indeed, item 2 sweeps the four prefix ones (4 transitions), item 6
creates two new ones to their left (4), and item 7 creates the four-one
prefix (11). The converted old prefix supplies two additional pairs.

For v >= 1,

`R(k,v) -> R(k+3,v-1)` in `6k+22` transitions.

Apply item 1 k times (4k), then item 4 (3). E now scans the last of
`2k+4` consecutive ones. Item 2 sweeps them left (2k+4), producing
`k+2` pairs. The bounce supplied one additional pair, so the suffix
now starts with `k+3` pairs. Items 6 and 7 (4+11) establish the next R.

Finally,

`R(k,0) -> E(2k+4)` in `4k+2` transitions,

by k applications of item 1 and then item 5. Induction on v therefore
proves, for every k,v >= 0,

`P(0,k,v) -> E(2k+6v+8)`

in `9v² + (6k+37)v + 4k+29` transitions. This is a universal word
calculation, not an extrapolation from sampled simulations.

## Resulting C rules

Let `d=(b+9)/2` and `v=(b+3)/2=d-3`.

For a >= d, entry followed by v interior P loops reaches
P(a-1-v, b+4, 0), whose u is at least 2. Thus

`C(a,b) -> C(a-d, 2b+11)`

in `(3b²+36b+121)/2` transitions.

For a = d-1, the same loops reach P(1,b+4,0), giving
E(2b+14), equal to E(3b-2a+21).

For `1 <= a <= d-2`, apply a-1 interior loops. They reach
P(0, 2a-1, (b+5)/2-a). Its universal boundary rule gives
E(3b-2a+21). Summing the finite transition counts, including the u=1
case, gives the common rule

`C(a,b) -> E(3b-2a+21)` for `1 <= a < d`,

with time
`3a² - (3b+42)a + (9b²+156b+683)/4`.

The E parameter is always even and at least 16, so it satisfies the
preconditions of the separately derived E/D lemmas in
`candidate_theory_c10.md`.

## Consequence with the E/D lemmas

Combining these universal C rules with those E/D rules gives the return
map stated in `candidate_theory_c10.md`. For
`S_j = 6*2^j-j-6`, an integer a strictly between S_j and S_(j+1)
returns from C(a,1) to C(24*2^j-9-j-a,1). Its new a is strictly
between S_(j+1) and S_(j+2). Both margins are positive for every j >= 0.

The literal blank startup reaches C(2,1), and `0=S_0<2<S_1=5`.
Every finite macro computation therefore returns to another positive-a
C configuration in the next interval. The only halting C case, a=0,
is never reached, and the constituent transition sequences do not halt.
This proves C10 nonhalting, given the independently derived E/D lemmas.
