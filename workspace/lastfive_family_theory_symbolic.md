# Symbolic terminal-tail certificates for C14

These are exact parameterized computations, not fits to sampled runtimes.
The initial C14 A boundary reached from blank at step 17 has prefix 111,
terminal tail 01, and A head -3. Write a general boundary as

    ...000 A>0 P (011)^k 01 000...,    k >= 0,

where P is a fixed finite bit word. The engine stores P exactly and keeps k
symbolic. Every ordinary transition reads a stored prefix cell. It never
substitutes zero for an unknown tail bit.

## Universal tail fold

Suppose H scans coordinate T at the beginning of (011)^k01 and cell T-1
is zero. All tape strictly left of T-1 is arbitrary. After 18+12k C14
steps, the configuration has:

- A at T-2, without reading that final head cell;
- three ones at T-1, T, T+1;
- the same tail (011)^k01 beginning at T+2;
- every cell strictly left of T-1 unchanged.

For C16, the time is 16+12k and the tape/head outcome is identical.

Proof: H transforms each 011 to 100 in five steps, and the final 01 to 10
in four. The right blank reset costs seven steps for C14 or five for C16.
A then makes k+1 seven-step carries to the left. The first starts at a
two-one run and the rest at three-one runs; each G0 sees a verified zero
and shifts A left three cells. Each subsequent carry leaves a two-one
run behind it. The last G0 reads exactly the supplied zero at T-1. These
operations give k copies of 011 to the right of the new three-one run,
followed by 01. Total: 5k+4+7+7(k+1)=18+12k.

## Why each successful map is universal

A map tracks time a+b*k and a tail count k+offset. Applying the tail fold
adds 18+12*offset to a and 12 to b. The symbolic tail shifts by two cells;
the prefix cells that it leaves behind are written explicitly.

If another state reaches an unknown tail cell, the optional unrolling
operation makes one 011 block explicit and replaces the count by
k+offset-1. This is legal only when k+offset>=1. The engine records that
condition by raising minimum input k to at least 1-offset. It consumes no
machine steps. The main actual-blank chain checks every recorded lower
bound against its known exact tail count before accepting a map.

At the next A left boundary, all known ones lie to A's right. The old
unknown tail remains farther right. Any explicit final 011 blocks can
be absorbed back into k, producing a constant offset. Thus a completed
certificate states, for every k at least minK, an exact output prefix,
tail-count offset, affine time a+b*k, and head displacement.

The first seven completed C14 maps require no unrolling: all have minK=0.
The map outputs therefore hold for every nonnegative k. The implementation
is in lastfive_family_theory_symbolic.js and exports makeMapper for an
independent wrapper or replay. The source table and tail-fold constant must
match: C14 uses 18, C16 uses 16.

## Bounded run and limitations

The saved JS prototype run used a 50-second wall limit. It completed seven
universal maps from the blank seed, reaching an A boundary at exact step
429755 with terminal-tail count 181. It then hit the time cap while deriving
the next map. The stop is recorded explicitly in the JSON. No repeated
prefix was found and no nonhalting classification follows from this bound.

The previously reached boundaries 55,156,294,1579,6906,181961 agree with
ordinary literal observations. The engine also reproduces the artificial
prefix [3,2,3,4] halter as 11020+648k C14 steps for the family with k terminal
two-runs; at k=0 this is the C14 analogue of the parent's 10910-step C16
example. Artificial inputs are not asserted reachable from blank.

The framework turns whole families of unbounded tapes into checkable finite
computations. A future repeated prefix with a nonnegative tail-count change
would require checking its minimum-k conditions through the whole cycle
before an induction proof could be claimed.

The first prototype did not retain the unfinished eighth map's tape and head;
that partial computation would require replay. All seven completed maps are
preserved, with explicit full bit words in
lastfive_family_theory_symbolic_fullprefixes.json. The standalone mapper now
returns complete tape/head/tail/time checkpoints on time or work caps. A future
run can pass such a checkpoint as the fourth argument to its map function,
using a newly constructed mapper with a fresh deadline. No replay of the old
unfinished map was performed for this update.
