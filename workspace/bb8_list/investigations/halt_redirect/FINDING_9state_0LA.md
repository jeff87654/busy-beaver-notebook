# 9-state candidate from the BB(8) record's halt redirect (2026-10-07, lead)

Machine (9 states, I0 undefined = the halt):

    1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA

It is the BB(8) record `1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1LF` (proofs/BB8_champ35_1RB0RA.v,
halts on E0 at its first list exhaustion K(0^35; 0; B), 2B+4 = 2^^37 3 i.e. arrow 37 2 3, score 24B+107)
with E0 := 0LI and a new state I = `---0LA`. Up to the first E0 the run is the record's run exactly.

## Notation (hyb10 / follow2 D-tokens)
D(m) = (10)^m 1. A configuration is a word of tokens with the head on the blank right of it in state G.
Champion digit d = D(3d+1) (D1 = zero digit, D4 = one); accumulator r = D(3b). Last three tokens before the tail are
[a | r], tail = D4. Rules (BB(8) record's R1-R3 in these terms, checked literally in these contexts):
- R1 [L | m+3 | r] -> [L | m | 2r+6]
- R2 [.., X+3 | 1 | r] -> [.., X | 2r+7 | 0]
- R3 [.., Y+3, 1^k | 1 | r] -> [.., Y, 2r+7, 1^(k-1) | 1 | 0]   (k >= 1)
Tokens with residue != 1 mod 3 are counters too (X+3 -> X); D0, D2, D3 block a borrow (event).

## Stage chain (follow2.py with --template R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=10101 --n 35; log f_0LA.log)
B = the record's final accumulator, B = 1 mod 5, B = 6 mod 7, B = 16 mod 25 (numres: B = 16537583495166 mod 18101949465600).
1. Stage 0 (literal): K(0^35;0;B) -> [D9^((12B+8)/5), D8, D6, D4^((24B+186)/5), D1 | D37 | D18] D4.
   (E0 -> I -> I1 = 0LA re-enters the record's start-up machinery; the 35 zero digits become ones, ~4.8B of them.)
2. Jump 1 (abstract champion process, full cycle): clears the D4 list; the borrow from D6 (R3, -> D3) refills;
   the process ends when the borrow reaches D3: [D9^x, D8, D3, D1^(k+1) | D1 | D(R1)] D4, k = (24B+186)/5.
3. Stage 1 (literal): [.., D8, D3, D1^m | D1 | D(r)] -> [.., D8, D0, D(2r+4), D4^(m-2), D1 | D37 | D18] D4.
4. Jump 2 (full cycle): clears D(2R1+4) (a digit: R1 = 0 mod 3) and the ones; ends at the D0 block:
   [.., D8, D0, D1^m' | D1 | D(R2)] D4, m' = (24B+191)/5.
5. Stage 2 (literal): halts in state I reading 0 (I0 undefined) for every m' except m' in {0, 7};
   real m' = 4 mod 7. ones = 2*R2 + (744B + 2121)/25 (exact for B = 16 mod 25).

## Independent literal checks by the lead (verify_0LA.py, reach.exe, ktrace.exe)
- Stage 0 target configuration reached exactly for b = 1, 6, ..., 196 (40 values).
- R1/R2/R3 on ~300 random constructed configurations in both left contexts ([D9^x D8 D6 ..] and [D9^x D8 D0 D(2R+4) ..]),
  plus R3 borrowing from D6 (-> D3) and from D(2R+4) (-> D(2R+1)), x in {0,4,16}, k in {1,2,5,9}: all exact.
- Stage 1 for x in {0,1,4,16,40}, m in {2..8,11,19,43,67}, r in {0..90} (multiples of 3): 440/440 exact.
- Stage 2: grid x in {0,3,7,12,20}, m in 0..63, r in {0,9,33}: halts in I reading 0 except m in {0,7};
  ones formula matched 32/32 cases with b = 16 mod 25 (3 more only ran out of budget).
Status: STRONG EVIDENCE (follower + independent literal checks). The abstract parts are the two champion-rule clearings.

## Size
Each cycle clears a list of ~4.8B ones with 2B+4 = 2^^37 3 (37 Knuth arrows). Our BB(9) record clears ~12B9 ones with
2B9+4 = 2^^13 3. So this machine is far above the BB(9) record (sigma ~ f_omega-level with index ~4.8B vs ~12B9).
A 10-state padding (state J unused) would also be compared against the BB(10) champion (> f_omega^2(25)).

## Siblings (2026-10-08 early morning)
The same redirect (E0 := 0LI, I = ---0LA) applied to the other three 35-digit machines (follow2, logs in
bb10_bb7_descendants/logs/):
- `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LH_---0LA` and
  `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LA`: exact twins of 0LA (2 full cycles, same ones formula).
- **`1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA` (F/H relay sibling): THREE full cycles.** Tail (10)^4
  instead of D4; canonical state F. Stages 0-1 as above. Stage 2: [D9^x, D8, D0, D1^m | D1 | D(R2)] ->
  [D9^(x-1), D8, D(2R2-18), D0, D4^(m+40), D1 | D37 | D18] (borrows one D9, rebuilds a longer list); jump 3 clears it
  (event at D0); stage 3 halts in I reading 0, ones = 2*R2 + 13/5*R3 + (816b+4224)/25. Still omega-level 1, strictly larger
  than 0LA. Literal checks: verify_fh.py (running).
- Independent confirmation of the 0LA chain by the other lead session (agent inv-bb10-c35-rebuild, own tools
  stage35.exe / stage2chk.py, investigations/bb10_c35_rebuild.md).
- Score comparison (agent inv-redir-score): score_comparison.md. Conditional on the stage chain, 0LA beats our BB(9)
  record, the BB(10) champion's actual (Coq) score and the peer's 10-state candidate 0LJ0LC; the peer candidate beats
  the BB(10) champion (tight one-arrow U lemma, section 6/6a).
- **Literal checks of the three-cycle sibling (lead, verify_fh.py / verify_fh_s3*.py, reach2.exe / ktrace2.exe):**
  stage 0 (40 b), ~300 rule checks, D6 and big-token borrows, stage 1: all exact. Stage 2 is
  [D9^x, D8, D0, D1^m | D1 | D(r)] -> [D9^(x-2), D8, D(2r-18), D0, D4^(m+40), D1 | D37 | D18]: TWO D9 are used (the follower's
  (12b-2)/5 = x-2; my first target said x-1); exact for x in {2,4,16,40}, m in {2..67}, r in {30,63,90} (r = 9 gives
  D(0) and halts: edge case, the real r is huge). Stage 3 in the real residue class (b = B mod 400/2800, R2, R3 = the
  universal accumulator residue mod 1200/3600): 12/12 halt in I reading 0, and for R3 >> R2 (10 more cases) always halts,
  with ones = 2*R3 + (terms in R2 and b): the follower's 13/5*R3 coefficient is a fitting artifact of independent
  representatives (R3 < R2 cases); halting and the dominant term 2*R3 are unaffected.
- Tool note: reach.exe / ktrace.exe assumed the tape left of the head ends in 1; for tails ending in 0 use reach2.exe /
  ktrace2.exe (same results on 0LA).

## 2026-10-08 02:10 check-in
- All three agents had stopped at ~01:19 (session limit); resumed by message at 02:10. No BB9_redir_0LA.v yet.
- Re-grade of the peer's 241 mf35 halters (regrade241.tsv, 157 done): 12 more 2-cycle omega-level-1 halters (0LA + J
  variants); none better than the three-cycle sibling so far.
- Sibling 9-state follow (f9sib_results.tsv, 29/357 done):
  - `1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0RB`: 9-state f_(omega+1)-SHAPE INFINITE REBUILDER (block
    event D2 -> D(2R+4); left event rebuilds D8 D4^(4R+n+8); level 3 after 6 cycles; no residue dependence, I0 never
    reached). A halting relative would be f_(omega+1) at 9 states.
  - `..._0RG1LD_1RH1LG_1LC0RG_---0LH`: >= 10 level-1 full cycles, using tokens next to its D9^(~2.4B) run as a counter;
    if it halts when they run out it is ~f_(4.8B+1). Followed for 60 stages: f_gh_0LH_60.log.
- Corrections from the Coq agent (02:xx): (1) the borrow from D3 is an ordinary R3 step (the "stage 1 event" is a
  champion-rule snapshot); (2) the final stage needs only m' = 0 mod 5, i.e. B = 16 mod 25 (2B+4 = tower = 36 mod 50);
  the mod-7 / {0,7} exceptions concern other residues. Real path: c_end -> Kr(1^(2n+34) 7 6 8 9^n) 1 0 -> b3 =
  U K (U K (U K 0)), K = 2n+35 -> halt in I on 0 with ones 6 b3 + 10n + 6K/5 + 23 = 3*arrow(K+2) 2 5 + 10n + 6K/5 + 11.
  Machine-level Coq part (dev/M.v, 180 KB) compiled 01:54.

## NEW LEAD (2026-10-08 ~03:00): the D9-counter machine, about B full cycles
`1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH` (9 states; G/H-swap sibling + E0=0LI, I=---0LH).
- follow2 (f_gh_0LH_60.log): >= 8 level-1 full cycles; tokens next to D9^((12b+3)/5) act as a counter; the zero list
  D1^((24b+191)/5) shrinks by 5 every 2 stages.
- Mini-follower (mf/mf35g.py family GH, single representatives): HALTS in I reading 0 after 298 stages (b0 = 6) and
  1155 stages (b0 = 46): ~21 stages per unit of b -> ~21B stages in the real run, the early ones full cycles over lists
  of length ~cB. Score class ~f_(4.8B+1) if it holds at the real residues (b0 = 166 run pending).
- Independent verifier dispatched: inv-gh0LH-verify (report halt_redirect/gh0LH_verify.md).
- **D9-counter machine verdict (fable-gh0LH, gh0LH_fable.md): HALTS** (high confidence): ~22.6 B stages, ~8.8 B full cycles
  at decreasing depth <= K+1 (K = (24B+191)/5), sigma between f_(K+2)^11(2) and f_(K+3)(9B), ~2^(K+2 arrows)(9B). No M3 trap
  (parked huge tokens are only consumed by champion jumps). Endgame confirmed u = 40..520 (real class u = 16 mod 504).
  All 'T' in size-ordered runs were budget effects (calibrated on 0LA's twin at 1.5e9). Opus verifier report pending.
- **9-state ranking (paper, conditional on chains):** BB(9) record < 0LA (3*2^(K+2 arrows) 5) < D9-counter (~f_(K+3)(9B))
  < three-cycle sibling (~f_(K+42)(small): third clearing at depth K+41). All below the peer's 10-state M3.

## PROVED (2026-10-08 ~05:00): 0LA halts and beats our BB(9) record (Coq, no axioms)
- proofs/BB9_redir_0LA.v: `halt : halts tm c0`; check.py PASS re-run by the lead
  ("PASS BB9_redir_0LA.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA HALTS (machine-checked, no axioms)").
- proofs/BB9_redir_0LA_bound.v (agent inv-bb9-redir-coq): score_exact ones = 6 b3 + 10 nn + 6 (KK/5) + 23,
  score_closed = 3*arrow (KK+2) 2 5 + 10 nn + 6 (KK/5) + 11, nn = (12 bf + 8)/5, KK = 2 nn + 35, 2 bf + 4 = arrow 37 2 3;
  halt in I on 0, so the standard score is ones + 1. All Print Assumptions closed.
- proofs/BB9_redir_0LA_vs_record.v (lead): arrow_agree9 + `redir_0LA_beats_record : exists cr Nr co No,
  c0 -[ BB9_record_1RB0RA.tm ]->* cr /\ halted .. cr /\ BB9_record_bound.ones cr Nr /\ c0 -->* co /\ halted tm co /\
  ones co No /\ Nr + 1 < No` — compiled 52 s, Closed under the global context.
- Report: investigations/bb9_redir_0LA_coq.md. Next: the same for the three-cycle sibling (agent continuing).
- **D9-counter machine, second verdict (inv-gh0LH-verify, gh0LH_verify.md):** HALTS after exactly (77B+413)/5 champion clears in
  one round (phases: 7-stage zero-list period, block eating, D9 eating; endgame [8 0 | 1 | R342] -> halt, ones =
  2 R342 + 2 R343 + 52), checked in the real class b = 6 mod 10 incl. b = 3366, 7566 (T = (77b+413)/5 exactly); 2-adic
  matching to mod 2^12 at the end. Score ~ f_(m0+1), m0 = (24B+191)/5: below the three-cycle sibling, above 0LA.
  Both verifiers (Fable, Opus) agree. Earlier mini-follower rebuilds were artefacts of r = 19 reps / b = 1 mod 10.
