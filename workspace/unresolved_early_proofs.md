# Universal nonhalting proofs for C05 and C06

These proofs concern the exact eight-state binary machines in `discovery_holdouts.txt`, with state A on an all-zero two-sided tape initially. A transition to Z halts. The machines differ only in F0:

- C05: `1RB1LA_0LA0RC_1RA1LD_0LE0LF_0LG0LD_1LE0LE_1RH1RZ_1RH1RB`
- C06: `1RB1LA_0LA0RC_1RA1LD_0LE0LF_0LG0LD_0LC0LE_1RH1RZ_1RH1RB`

The distinction is F0=1LE (C05), versus F0=0LC (C06). Their common transitions are A0=1RB, A1=1LA, B0=0LA, B1=0RC, C0=1RA, C1=1LD, D0=0LE, D1=0LF, E0=0LG, E1=0LD, F1=0LE, G0=1RH, G1=1RZ, H0=1RH, H1=1RB.

## Notation

A(n,m;v) is the configuration with state A on a blank immediately left of the word `1^n 0^m 1 v`. All cells left of the head are zero. The finite suffix v, including any trailing blank convention, is arbitrary and remains untouched in the lemmas below. Translation of the whole configuration is immaterial. In a transition sequence, `D1` means execute D's read-1 transition, rather than a state/tape pair.

E(d,r,m;v) has state E on position 0, zeros through position d-1, then `1^r 0^m 1 v` starting at d, and zeros to the left. The E notation permits m at least 1. The shared sweep and r=1 lemmas require only m at least 1; the r=2 boundary requires m at least 3. The proof uses d congruent to 1 or 2 modulo 3. The same E lemmas also apply to a run followed only by blanks, but that is unnecessary here.

## Shared sweep lemmas

For n at least 2, A(n,m;v) reaches E(4,n-1,m;v) in exactly 6 steps, through

`A0 B1 C1 D0 E1 D0`.

The new E head is three cells left of the old run's first cell; the first surviving one is the old run's second cell.

For r at least 3, start from E(d,r,m;v). The sequence

`E0 G0 (H0)^d H1 B1 C1 D0 E1`

ends in state D immediately left of the erased first old one. It leaves a newly filled run of d+1 ones, at positions -1 through d-1. Repeated `D1 F1 E1` transitions erase that run moving left. If d is 1 modulo 3, erasing the run ends in E on position -2. If d is 2 modulo 3, it ends in D on position -2, and one D0 step reaches E on position -3. Therefore:

- d congruent to 1 mod 3: E(d,r,m;v) -> E(d+4,r-2,m;v), taking 2d+8 steps.
- d congruent to 2 mod 3: E(d,r,m;v) -> E(d+5,r-2,m;v), taking 2d+9 steps.

Beginning with d=4, after q iterations the distance is

`d_q = 4 + 4q + floor(q/2)`.

The q-th iteration, numbering from zero, costs 9q+16 steps. The first q iterations cost `(9q^2+23q)/2` steps. Their distances alternate between 1 and 2 modulo 3, so every iteration satisfies its stated precondition.

For r=1, execute

`E0 G0 (H0)^d H1 B0 (A1)^(d+2)`.

The result is A(d+2,m;v) after 2d+6 steps. It preserves the entire suffix and gap.

## The r=2 boundary, with m at least 3

From E(d,2,m;v), first execute

`E0 G0 (H0)^d H1 B1 C0`.

After d+5 steps, the tape has a run of d+2 ones at -1 through d, a zero at d+1, a one at d+2, and state A on the blank at d+3. The old isolated one at d+m+2 and its suffix have not been touched. Since m is at least 3, the cell d+4 is also blank. Execute

`A0 B0 A1 A1 A0 B1 C1 D0 E1`.

After these 9 steps, D is at d and the tape consists of the d+2-one run from -1 through d, a new isolated one at d+3, and the unchanged old isolated one at d+m+2 with suffix v. The gap between those two isolated ones is m-2.

Erase the left run by the left-moving cycle `D1 F1 E1`.

If d is 1 modulo 3, its length d+2 is divisible by 3. The erasing cycle ends in D on blank position -2; D0 then gives E on -3. This is E(d+6,1,m-2;v), reached after 2d+17 steps from the original E configuration. Apply the r=1 lemma to obtain A(d+8,m-2;v), for a total of 4d+35 steps.

If d is 2 modulo 3, the length d+2 is 1 modulo 3. Erasure ends in F on blank position -2, after 2d+16 steps. The final finite sequence depends on the machine:

- C05: `F0 E0 G0 H0 H1 B0 A1 A1 A1` (9 steps). It produces a three-one run at -4 through -2 and A on -5.
- C06: `F0 C0 A0 B0 A1 A1` (6 steps). It produces a two-one run at -3 through -2 and A on -4.

Thus the resulting normalized word is `1^c 0^(d+4) 1 0^(m-2) 1 v`, where c=3 for C05 and c=2 for C06. Total times are 2d+25 and 2d+22 respectively. No listed sequence executes G1, the sole halting transition.

## Resulting universal A maps

Combining the entry, repeated sweeps, and boundary steps gives the following for every m at least 3 and arbitrary suffix v:

| Input n | Output word after A's left blank | Steps |
| --- | --- | --- |
| 4k, k>=1 | `1^(9k+1) 0^m 1 v` | `18k^2+23k+3` |
| 4k+2, k>=0 | `1^(9k+6) 0^m 1 v` | `18k^2+41k+20` |
| 4k+3, k>=0 | `1^(9k+12) 0^(m-2) 1 v` | `18k^2+59k+57` |
| 4k+1, k>=1 | `1^c 0^(9k+3) 1 0^(m-2) 1 v` | `18k^2+23k+22` for C05; three fewer for C06 |

For completeness the final row also holds for k=0. Starting with n=1, the direct prefix `A0 B1 C0`, then the same nine-step A sequence above and D1, reaches F on the same left blank. This takes 13 steps; the corresponding 9- or 6-step finish gives 22 or 19 steps.

These are universal transition identities, obtained from the explicit cycles and boundary transitions above. The finite grids in `unresolved_early_proof_checks.json` are corroboration, not the justification of universality.

## C05: an expanding invariant family

Let X_j be A on the blank immediately left of

`1^3 0^327 1 (0^323 1)^j`, for j>=0.

Literal simulation of the exact machine from blank reaches X_0 at step 30,517. The universal maps give, retaining the arbitrary suffix `(0^323 1)^j` throughout:

1. A(3,327;v) -> A(12,325;v), in 57 steps.
2. A(12,325;v) -> A(28,325;v), in 234 steps.
3. A(28,325;v) -> A(64,325;v), in 1,046 steps.
4. A(64,325;v) -> A(145,325;v), in 4,979 steps.
5. A(145,325;v) -> A on `1^3 0^327 1 0^323 1 v`, in 24,178 steps.

Consequently X_j -> X_(j+1) in exactly 30,494 steps, with head displacement -324, for every j>=0. The recurrence never uses G1. Induction proves that C05 does not halt. In particular the reached times are `30,517 + 30,494 j`; the tape has j+4 ones at those times. The tape is not cycling: a new isolated one is added each period.

## C06: a second expanding invariant family

Let Y_j be A on the blank immediately left of

`1^2 0^210 1 (0^204 1)^j`, for j>=0.

Literal simulation from blank reaches Y_0 at step 12,631. The universal maps give:

1. A(2,210;v) -> A(6,210;v), in 20 steps.
2. A(6,210;v) -> A(15,210;v), in 79 steps.
3. A(15,210;v) -> A(39,208;v), in 396 steps.
4. A(39,208;v) -> A(93,206;v), in 2,046 steps.
5. A(93,206;v) -> A on `1^2 0^210 1 0^204 1 v`, in 10,070 steps.

Thus Y_j -> Y_(j+1) in exactly 12,611 steps, with head displacement -205. Induction again proves nonhalting. The reached times are `12,631 + 12,611 j`, with j+3 ones.

## Independent finite checks and scope

`unresolved_early_proof_checks.py` contains its own literal transition parser and set-based simulator; it does not import an accelerator or previous simulator. It checks the exact blank seeds, the predicted macro result and exact time for 1,600 parameter/suffix cases per machine, and the first eight expansion instances of each family. Source machine strings are included in the output. The standalone proof is the universal phase derivation plus the finite blank prefix, not a large-step cutoff. C03 is not classified by this argument.


## A shorter independently checkable locality proof

A second proof uses a literal finite execution as a compact certificate. For C05, specify only state A on position -1, all negative cells blank, and positions 0 through 7 equal to `11100000`; leave every cell at 8 or beyond completely unspecified. A literal execution for 30,494 transitions reads/writes only positions -324 through 7, and ends in A at -325. Below -316 the resulting tape is exactly ones at -324,-323,-322 and zeros elsewhere: the same known prefix and blank left half-line translated left by 324. The remaining tape can again be arbitrary. Thus the partial configuration reproduces itself and induction gives an infinite execution. No extrapolation about an unread cell is involved.

For C06, use prefix `110000000` at positions 0 through 8, with the unknown suffix starting at 9. After 12,611 transitions, reads/writes have stayed in -205 through 8, the state/head are A/-206, and below -196 the only ones are -205,-204. This is exactly the same partial configuration shifted left by 205. The literal blank seeds already checked above satisfy both minimal prefix conditions.

`unresolved_early_locality_minimal.py` checks these partial-configuration certificates with an explicit rejection on any unknown-cell read. It also rejects three malformed cases per machine: an unknown boundary one cell too close, a cycle time one step short, and an initial transition changed to halt. `unresolved_early_locality_minimal.json` records all bounds and outcomes. This locality check is a finite proof of the arbitrary-suffix recurrence, not merely a test on finitely many suffix samples.

