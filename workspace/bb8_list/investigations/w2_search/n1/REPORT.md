# w+2 search, n1 base: report (Opus investigator, 2026-10-09)

## Result in one paragraph
I found no Tier-1 or Tier-2 halter in 12-13 states. I did find the n1 analog of G6:
**L12, a 12-state machine whose rounds restart cleanly.** At every exhaustion it deletes the far region and re-enters
n1's own round start [2 5 1^(4R+3) 0^3 9 1^n]. The new counter comes from the accumulator R, and the depth n is kept.
This gives f_(omega+2)-shaped rounds (u_(i+1) ~ f_(omega+1)(u_i)), but L12 never halts.
I also found a 13-state machine (M13a) whose restarts depend on the residue class of the counter.
Every restart mechanism found uses all of its free slots. In the 13-state searches (about 160k follower leaves, partial
coverage) no leaf halts after a restarted round. Clean restarts make all rounds identical modulo 10080, so they
cannot count rounds at all (argument below).
Evidence level: follower screening (std policy, real start b0 = 6 and constructed starts) plus literal stage runs.
No Coq.

## Machines
- **L12** = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC1LL_0LK0RC
  (J0 = 0LK, K = 0LC1LL, L = 0LK0RC; all slots defined, no halt).
  - Real start, b0 = 6 (log L12_b6.log): rounds start at stages 0, 47, 94 and 141. Each start is exactly
    "2 5 1^79 0^3 9 1^n", with depth n = 32, 472, 912 and 1352.
  - Mechanism: one J0 pass turns most of the far D2 run into a few big digit tokens (k = 17: 2^10 -> "26 33"). The
    champion process consumes these by full clears. Then "7 1^N" -> left event at blank -> H, which is n1's own
    no-far restart. The counter is 4R+3, where R is the accumulator of the left event (H event spec).
  - Robustness: start far_k + [0 1^30|1|19]:
    - Clean restart at stage 10 for every k = 1,2 mod 3 with k >= 7 (also k = 3, 4).
    - Junk for k = 0 mod 3 and for k = 2, 5.
    - The real class is k = 2 mod 3 (k_end = 17 in the follower).
    - Depth n = 28..37 all restart cleanly; the start R is irrelevant.
  - Round ends by counter class (cscan.py): c = 9 mod 14 with c != 9 mod 42 restarts; c = 9 mod 42 (k = 0 mod 3)
    gives junk.
- **M13a** = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LC0LL_0LA1RM_0RM0LE
  (13 states, no halt).
  - Start far_17 + [0 1^41|1|19]: it restarts with a counter of 2*depth - 52 (std 142; big policy 13582 = 2*6817 - 52)
    and keeps the depth.
  - Round 2 ends in another class and restarts in place: the D2 run becomes a digit 78, which stays as a prefix
    "78 6 2 5 1^33 ...".
  - cscan: it restarts for most counter classes, with varying counters (79, 142, 169, 179, 1689, 13, 11, ...).
  - All 7 new slots are read by the first restart (dropslot.py), so there is no spare slot for a halt.
- An 11-state sibling (J0 = 0LK, K = 0LC1LJ) restarts cleanly with counter 91. Round 2 then ends in a junk class
  (91 = 7 mod 14), and junk never reads J0.

## Why clean restarts cannot give Tier 1/2 (structural)
1. The restart that comes for free (the no-far world: [0 1^n|1|R] on a blank left side) is n1's own H/unpack. H writes
   the new counter LEFTWARDS over about 6R cells. So the far region (D2^k + 44-bit tail) must be erased completely
   first, and no marker (d) can survive to the left.
2. After a clean restart, round i+1 has counter 4R+3 with R = 19 mod 2520 (the fixed class of the accumulator).
   Round 1's counter at S0 is 6T-17 = 79 mod 10080 as well. So every round end has the same k, the same counter class
   and the same far tail modulo 10080. A gadget acting at the far tail behaves identically every round and cannot
   halt at round 2 without halting at round 1. The only quantity that differs between rounds is the depth n (its
   residue mod 3 cycles: 472, 912, 1352). Reading it would need a mod-p walk over the whole depth list, which 1-3
   states cannot do on top of the eater.
3. Even without erasing, the round's own D2 run (k ~ 0.29 x counter) separates the round-end event (J0 at tail idx 22)
   from anything older to the left. So d cannot sit to the left either.
4. The remaining Tier-1 route is in-place or residue-varying restarts (M13a-like): the round-2 counter class differs,
   and a slot read only at that class's round end would be the halt. It needs a restart mechanism with a spare slot.
   None was found: every restarter found uses every new slot. The one exception is a family of 13-state clean
   restarters with M1 never read (for example ..._0LK0LC_0LC0LL_0LL0LM_1RE---), but its rounds are identical, so M1
   is never read.

## Searches (all J0 completions of n1; leaves = follower or literal runs)
| search | start | size | outcome |
|---|---|---|---|
| exp1: J0 -> existing state (10 states) | real start b0=6, 120 stages | 40 | no proper round restart |
| genum.py ns=1 (follower) | far_5 + [0 1^60/1/19] | 2828 leaves | in-place messy restarts only |
| lenum literal ns=1 / ns=2 | far_4 + [0 1^5/1/19] | 1805 / 64.6k leaves | no direct no-far K-moment (needs follower stages) |
| genum3 multi-k clean restart ns=1; ns=2 J0=0LK/1LK partial | k-sets incl. 2,3 | 3433 + ~17k nodes | 0 pass (k-sets too strict, see note) |
| genum2 ns=2 J0=0LK | far_5, n=60 | 9973 leaves | led to the L12-type observation |
| **genum5 ns=2 J0=0LK** | S37 input far_17 + [0 1^329/1/19] | 13459 leaves (nearly complete) | restarts: L12 family (c=79), c=91 junk family, 2 prefix types; **0 HALT after a restarted round** |
| genum5 ns=2 J0=1LK | same | 11112 leaves (partial) | no restart at all |
| **genum5 ns=3 J0=0LK, K0=0LC** | far_17 + [0 1^41/1/19] | 42239 leaves (partial: K1 up to the 0LL subtree) | 97 leaves with restarted rounds (M13a; clean c=79 with spare unread M1; P10 far-sized counters 1669); **0 HALT after a round** |
| genum5 ns=3 J0=0LK, K0=0LA | same | 80089 leaves (partial) | 9 with rounds; 0 HALT after a round |
| n1 junk residues b0 = 11/16/21 | real start | 3 runs | 16-stage constant-growth junk cycle, never reads J0, not a restart |

Note: requiring all k in {2,3,...} in genum3 was too strict, because L12 fails at k = 2, 5 and k = 0 mod 3. Only
k = 2 mod 3 (k >= 7) matters for the real class. genum5 (real k = 17) replaced it.

## Tools (w2_search/n1/)
- sim.py: Python literal simulator for n1 gadget machines; far_of(k).
- gstage.cpp/.exe: stage35g generalised to 16 states.
- nfol.py: follower; supports --start and --fark.
- fstep.py: one follower stage as a function.
- show.py: whole-tape tokens at every K-moment.
- gtrace.exe: literal tracer.
- lenum.exe: C++ literal lazy TNF enumerator.
- genum*.py: lazy TNF enumerators.
  - genum5: period-signature chains; --fix seeds; Tier-1 leaf = HALT after a chain.
- sigs.py / per.py: round detectors.
- verify_restart.py: k-scan of restarts.
- nscan.py: depth / R scan.
- cscan.py: round-end outcome per counter class.
- dropslot.py: undefine each slot and follow.
- clonesplit.py: adds state M by clone-split.
- cs14.py: 14-state clone-split follower test (written, not run).
- NOTES.md: running notes.

## Follow-ups after the lead's requests (2026-10-09 ~17:00)
- L12 scaling confirmed: big policy (r = 2539) and shrink both give a clean restart at stage 10 with counter
  m = 10159 = 4*2539+3 (std: 79 = 4*19+3) and depth 13613 (std: 173). The reload is accumulator-sized and the depth
  jump scales; it is not an artefact of the representative.
- M13a's restart counter is DEPTH-sized (c2 = 2*depth - 52, checked under big policy) while the depth list is also
  kept. This is a possible d source for Tier 2: something rebuilt every round, inside structure the round creates.
- cs14.py on M13a (52 clone-split variants at 14 states, 300 stages): 0 halt after a restarted round. 7 variants never
  read their undefined symbol in 300 stages.
- Exact coverage of the stopped trees is in NOTES.md ("Exact coverage" section).

## Recommended next step
1. (Done: cs14 on M13a was negative within 300 stages.) A longer horizon (1000+ stages) for the 7 variants that never
   read their undefined symbol would test whether a later round class reads it.
2. Tier 2 on this base needs a counter d that survives restarts. With n1's leftward unpack, d can only live inside the
   kept depth list or in an in-place prefix (like M13a's "78 6"). That is a 15+ state design.
   The G6 slice may be the better base for Tier 2.
3. To finish the 13-state Tier-1 search, run genum5 ns=3 for every K0 seed (run_k0.sh; it resumes by skipping seeds
   marked done). About 50-100k leaves per seed at about 10 leaves/s.
