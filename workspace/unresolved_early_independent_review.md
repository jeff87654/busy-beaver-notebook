# Independent review of the C05/C06 nonhalting proof

Reviewed by the theory subagent independently of the proof author. I agree
with the universal transformations and the resulting nonhalting conclusions
in `unresolved_early_proofs.md`.

For E(d,r,m;v), r>=3, the shared prefix leaves exactly d+1 newly written ones
at positions -1 through d-1, with D at d-1. Clearing this run with the cycle
D1 F1 E1 ends in E at -2 when d=1 mod3, and in D at -2 when d=2 mod3. The
latter case uses one D0 to reach E at -3. The surviving old run starts at
d+2. This independently yields the stated new distances d+4 and d+5, and
the times 2d+8 and 2d+9.

At r=2, I traced all nine boundary transitions. They leave the run -1..d,
an isolated one at d+3, and the original isolated one at d+m+2. The
rightmost read is d+4, strictly before the original isolated one because
m>=3. Thus the original one and the entire arbitrary suffix v are
untouched. The run length d+2 determines whether erasure exits as D or F;
I checked both C05 and C06 finite F0 endings explicitly. In the d=1 mod3
case the following r=1 lemma needs only gap>=1, so it remains valid with
gap m-2. This minimal precondition has been sent to the proof author for
explicit clarification.

Every listed occurrence of G reads a zero: E0 enters the fresh blank on its
left, and the C05 special ending also enters a fresh left blank. The left
run-erasing cycle contains no G transition. Therefore the sole halting
transition G1 is excluded universally, including at both boundary cases.
The n=1 direct case also checks exactly: its first 13 steps end at F on a
left blank, followed by the respective nine- or six-step ending.

I independently substituted q=2k-1 or q=2k into
d_q=4+4q+floor(q/2) and the summed sweep cost. This reproduces all four A
map outputs and all four time polynomials. Summing the five maps gives
30,494 steps for C05 and 12,611 for C06, independent of suffix length.
The untouched old isolated one fixes the respective displacements at
-324 and -205. The appended gaps have lengths 323 and 204, as claimed.

As a separate finite seed check, a literal JavaScript transition loop
(independent of the author's Python) ran the blank prefixes and one full
expansion. The results are recorded in
`unresolved_early_independent_seeds.json`. C05 reaches its seed at step
30,517 with head -329; C06 at step 12,631 with head -209. Both subsequent
expansions have exactly the claimed tape, state, duration, and displacement.
These finite checks establish the base cases; the universal phase proof
and suffix preservation establish induction for every subsequent cycle.
