# C07 and C08: a nonhalting proof

The two machines on lines 7 and 8 of discovery_holdouts.txt are nonhalting. This is an inductive argument about every future cycle, not an extrapolation from a simulation cutoff. A separate mxdys RWL/CTL decider has independently certified the same result with its closure verifier and a fresh-process replay.

Write H(n,k) for the configuration

    0^infinity 1^n H> 0 1^k 0^infinity,

where the head scans the zero immediately after the left block. Both machines reach H(9,0) from blank tape after exactly 43 steps.

For every n = 1 (mod 4), n >= 5, and k >= 0, both machines obey

    H(n,k) -> H(2n-1,k+1).

The transition takes (2n+7)(n+1)/2 steps for C07 and two fewer for C08. It encounters no H state between its endpoints; its endpoint again reads zero. The only halt instruction in either machine is H1, so this proves nonhalting by induction. The successive left-block lengths are 9,17,33,65,..., namely 2^(j+3)+1 after j cycles. Their very large simulated step counts therefore measure a provably infinite expanding computation.

## Derivation of the recurrence

Define

    X(a,b;k) = 0^infinity 1^a F> 1^b 00 1^k 0^infinity.

The F head scans the first of the b ones. Direct use of the transitions gives these rules:

1. If a >= 4 is even and b >= 3, X(a,b;k) -> X(a+5,b-2;k) in 2a+24 steps.
2. If a >= 5 is odd and b >= 3, X(a,b;k) -> X(a+3,b-2;k) in 2a+4 steps.
3. If a >= 4 is even, X(a,1;k) -> H(a+5,k) in 2a+24 steps.

These rules do not use the one transition where C07 and C08 differ.

For an odd a, alternating F1/E1 steps sweep left through the a+1 ones and change them into (10)^((a+1)/2). F0 adds a leftmost 1 and turns right. Alternating G1/F0 steps restore each 10 pair to 11. A final G1 reaches the next F position. Counting these steps gives rule 2.

For even a=2r >=4, the leftward sweep instead ends in E on the left blank, with the word (01)^r 0 to its right. The fixed 26-step local identity is

    0^infinity E> 0 01010 W -> 0^infinity 1^8 G> W.

It never reads any cell of the arbitrary suffix W. Its complete 26-step state/head/read trace is in candidate_theory_certificate.json. Here W begins with (10)^(r-2), followed by 1^(b-1)00 and the old suffix. G1/F0 restores those r-2 pairs. For b>=3 the next G1 gives rule 1; for b=1 the next G0 enters H on the second separator zero, giving rule 3. The total is (a+1)+26+(a-4)+1 = 2a+24.

Finally, the H0 entry followed by a leftward A1 sweep and a fixed boundary routine gives

    H(n,k) -> X(4,n-4;k+1)

in n+14 steps for C07 and n+12 for C08. Their differing D1 instruction changes this entry path by two steps, with the same resulting tape.

Put n=4m+1. Apply rules 1 and 2 as a pair m-1 times, taking (a,b) from (4,4m-3) to (8m-4,1). Rule 3 then reaches H(8m+1,k+1)=H(2n-1,k+1). Summing the entry, paired, and final steps gives 16m^2+26m+9, equivalent to (2n+7)(n+1)/2, minus two for C08.

## Reproduction

candidate_theory_certificate.py checks the fixed local identity without reading its arbitrary suffix, the 43-step blank prefixes, and 978 finite instances of the stated rules/cycles using ordinary single-cell transitions. These checks support and catch transcription errors in the universal pair-sweep argument; they are not used as a substitute for induction.

