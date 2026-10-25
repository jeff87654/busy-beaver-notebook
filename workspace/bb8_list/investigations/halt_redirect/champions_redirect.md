# Halt redirect of the BB(9) and BB(10) champions (2026-10-08, Opus investigator)

## Verdict

**No record candidate for either target.** All 1-new-state redirect extensions fall into one of three classes:
1. they halt within 11 steps of the champion's own halt (at most one more 1 than the champion);
2. they cycle or translate forever near the end of the counter block, without rebuilding anything;
3. they rebuild a deep list from the huge counter and never halt.

| target | base (E0 left undefined) | new state | leaves | halt within 11 steps | cycler/runaway | deep rebuild, never halts | record candidates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BB(9) champion, 10-state ext. | `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH` | J | 164 (+36 with E0 into an old state) | 20 | 45 | 99 | 0 |
| BB(10) champion, 11-state ext. | `1RB1RA_0LC0LF_0RD1LC_1RA1RG_---0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ` | K | 180 (+40 with E0 into an old state) | 20 | 45 | 115 | 0 |

The rows with E0 pointing into an old state are trivially non-halting: every old transition is defined and the new
state cannot be reached.

The reason is structural, not just empirical. The redirect only changes the champions' used-up-list rule (R4) for odd b.
This family has a proved cap: a halting run makes **at most two deep clearings**. The cap is in section 4 of
`../bb10_champion_1RB1RA_0LF0LJ.md`, and both champions already use both clearings. A third deep clearing would beat both
bars easily, but any redirect that rebuilds a deep list returns to an R4 residue state it has already visited, so it
never halts (section 3).

## 1. The halting configuration (literal)

Both champions share every transition used from the used-up list `Kd [] 0 b = 0^inf [D on 0] 1^(b+1) 0^inf` to the
halt, so they have the same halting configuration:

    Kd [] 0 b  --(R4 odd)-->  0^inf 1 1 (0 1 1)^((b+1)/2) [E on 0] 0^inf        (b odd; E0 = 1RZ is the halt)

- **Checked literally** with `champ/hcfg.py`, which builds Kd [] 0 b, runs the champion to its E0 read, and fails
  loudly otherwise. It was checked for b = 1, 3, 5, 7, 9, 11, 23, 39 and 1687 on both machines. There are b+3 ones at
  the E0 read; b = 1687 takes 1,433,964 steps. b = 2 does not halt, as expected, because even b rebuilds.
- **Coq status.** Both champions' Coq proofs already prove this step (lemma `KR4Ox`).
- **The halting residue class.** In both runs the halting counter b2 comes out of a deep clearing, so it equals the
  2-adic/odd-modulus fixed point E. That fact comes from `modexact.py`/`hstab_odd.py`; its mod-8 part is Coq `U_mod8`.

| modulus | E (odd, halting class) | O (even, rebuild class) |
| --- | --- | --- |
| 2^16 | 55783 | 41712 |
| 2^24 | 1235431 | 14394096 |
| 1680 | 7 | 1120 |
| 6720 | 3367 | 2800 |
| 887040 | 184807 | 244720 |

So the enumeration starts used b = 7, 9, 11, 13, 23, 39, and the classification used b = 7, 13, 39. b = 7 is ≡ E mod
1680 and mod 32, and b = 39 is ≡ E mod 64. b = 9, 11, 13 and 23 are off-class controls.

## 2. What was enumerated

`renum.exe BASE NMAX st_small.txt 1e6 0` started from the literal halting configurations (`champ/all9.tsv`,
`champ/all10.tsv`). TNF branching defines E0 over all 40 or 44 values. When E0 = xyN, it then defines the first-reached
transition of N over all values, and the other transition of N stays undefined as the new halt.

Each extension was then classified three independent ways:
- **Literal Kd-moment tracer** (`champ/kcls.py`, 10^6 steps from the halting configuration, b = 7, 13, 39). It records
  the first `Kd ds a b` configuration after the redirect and the list length as b varies.
- **The BB(10)-relative grader** `../bb10_champion_1RB1RA_0LF0LJ/r10grade.py --list` (`champ/g9.tsv`, `champ/g10.tsv`).
  It works from the blank tape. It checks R1-R3 literally (all transitions they read are the champion's), fits R4 per
  residue class on b = 16..79 and validates the fit on b = 80..143. It then runs the residue dynamics.
- **Cycle and translated-cycler checks** (`champ/cyc.py`, `champ/tcyc.py`) for the extensions that never return to the
  Kd shape.

The three methods agree machine by machine. The grader's "runaway" sets equal the tracer's no-Kd sets, and the grader's
"cycles" sets equal the tracer's deep-rebuild sets, for both targets.

## 3. Behaviour classes

- **A. Quick halts (20 per target).** Examples are E0 = 0LJ with J = `------`, `---0RE`, `1LJ---`, and so on. They halt
  1 to 11 steps after the champion would, with 0 to 2 extra ones. The best is the champion's tape plus one 1 (12 vs 11 at
  b = 7). The grader rates them BELOW for BB(9) (`w^2(8)`) and EQUAL-key for BB(10) (`w^2(25)`, sigma = b2 + O(1)).
  Neither is near the next bar.
- **B. Cyclers and runaways (45 per target).** The new state and its one defined transition loop at the right end of
  the counter block.
  - 38 per target are translated cyclers: `tcyc.py` gives a record-to-record window match.
  - 7 per target are exact in-place cyclers from step 0 with period 2 to 10 (`cyc.py`), for example E0 = 0LJ with
    J1 = 1RE (period 2). They depend only on the block's last few cells, which are the same for every b.
  - All 45 hold on b = 7, 13 and 39. The grader independently marks the odd class NO-RETURN.
- **C. Deep rebuilds (99 for BB(9), 115 for BB(10)).** This is the idea working as designed. The new state routes into
  the champion's start-up or rebuild machinery, and the machine rebuilds a Kd list whose length grows linearly in b.
  - Literal list lengths at b = 7, 13, 39 are, for example, 10, 16, 42 (slope 1) and 9, 12, 33 (slope 3/4).
  - Example literal first moments:
    - BB(9) with E0 = 0LJ, J = `---0RA`: `Kd [(0,1)^n,0,0,0,2] 1 0` at b = 2n+1.
    - BB(10) with E0 = 0LK, K = `---0RA`: `Kd [1,(0,0,3)^(n+1),0,2] 0 0` at b = 4n+3.

    Both match the grader's fitted R4 for the odd class.
  - The list is then cleared by the champion's R1-R3. Those are Coq-proved for all parameters and never read E0, so the
    redirect does not disturb them.
  - Stage chain, BB(10) example, with residues mod 2^16 from r10grade -v:

        champion run: ... b1 = O (41712) -> champion rebuild -> b2 = E (55783)            [halt point of the champion]
        redirect: b2 = E, class 3 mod 4 -> Kd [1,(0,0,3)^(n+1),0,2] 0 0 (depth ~3b2/4) -> clearing -> b3 = E (55783)
        b3 = E -> the same redirect rebuild -> E -> ...  (R4 state repeats: never halts)

    For BB(9), with E0 = 0LJ and J = `---1LH`, the chain is O -> E -> redirect rebuild -> O -> champion rebuild -> E: a
    cycle.
  - Every class-C machine of both targets is graded "residue dynamics cycles (R4 states repeat)".
  - The general reason: any list whose deepest digit is at depth ≥ 3 clears to E or O. E (odd) leads back into the
    redirect, and O (even) leads to the champion's rebuild, which returns E. So once the redirect does one deep
    clearing, R4 states repeat.

## 4. Score comparison

- **BB(9) champion, 10-state extensions.** The bar is the BB(10) champion, f_ω²(25) = f_ω(f_ω(25)) (raw wikitext, fetched
  2026-10-08). The BB(9) champion is about f_ω(f_9(2)). A halting extension with a third deep clearing would reach about
  f_ω(f_ω(f_9(2))), which beats the bar, but no such extension exists (section 3). The best halting extension is the
  champion + 1 one, below the bar. Our own BB(9) record and the 9-state 0LA lead are already far larger than this
  champion.
- **BB(10) champion, 11-state extensions.** The bar is the BB(11) champion,
  `1RB1RA_1LH1RC_0LD0LG_0RE1LD_1RA1RF_---0RA_1LC1LG_1LJ1LI_1LK1LJ_1RZ0LI_1RA1LH`, with f_ω²(10↑⁴4) (raw wikitext:
  `f_\omega^2(10 \uparrow^4 4)`). The BB(10) champion's f_ω²(25) is below it, because f_ω(25) < f_ω(10↑⁴4). A third
  deep clearing would give about f_ω³(25), far above the bar, but again it never halts. The best halting extension is
  f_ω²(25) + 1 one, below the bar.

## 5. Evidence level and limits

- **Enumeration.** It is complete for the stated space: E0 over every value, plus the new state's first-reached
  transition over every value, with the other transition as the halt.
- **Verdicts.**
  - Class A is literal: the machines halt at b = 7..39 within 11 steps, uniformly in b.
  - Class B is literal cycler or translated-cycler certificates on b = 7, 13, 39 (this extrapolates to the huge b2).
  - Class C combines Coq for R1-R3, literal R4 fits validated on 64 values of b, and the computed 2-adic fixed points E
    and O, for which only mod 8 is proved in Coq. Status: **STRONG EVIDENCE of non-halting** for class C, not a proof.
  - Nothing in class C could halt even if the residue claims failed in a subtle way, short of the clearing ending
    outside {E, O}. Every grader run matched the tracer's literal first rebuild.
- **Not covered.**
  - Two new states: an 11-state extension of the BB(9) champion, or a 12-state extension of the BB(10) champion. The
    same cap argument applies to any redirect that acts on R4 through residues, so a winner would need a non-Kd
    structure.
  - Redirecting transitions other than E0.
- **Cost.** About 1.5 h wall time at Idle priority on a shared machine. That is two renum runs (seconds), the Python
  tracer (about 50 min each target, run in parallel), the grader (about 75 min per target, in parallel), and the cycler
  checks (minutes).

## 6. Addendum: the J0-free BB(10) variant as a second root

The lead suggested this root. In the EQUAL variant `1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_---0LG`
J0 is never read. Its R4-odd path reaches the same halting configuration (literal check at b = 7, 13, 39). With E0 left
undefined, `renum` was run from it:

| run | leaves | halt quickly | cyclers | deep rebuild | other | candidates |
| --- | --- | --- | --- | --- | --- | --- |
| 10 states (E0 into an old state, J0 stays the halt) | 40 | 3 | 12 | 25 | 0 | 0 |
| 11 states (new K; J0, K0 and K1 free) | 2508 nodes | 323 | 649 | 1530 | 6 | 0 |

- **10-state run.** All 40 were graded with `r10grade.py`. The 3 halters are EQUAL to the champion, halting at J0 with
  4n+6 or 4n+7 ones at b = 4n+3, the same as the champion or one fewer. They sit far below the current 10-state front-runner, the padded 9-state 0LA
  machine. The other 37 are NONHALT-PREDICTED: 12 runaways and 25 residue cycles. Output is in `champ/gv10.tsv`.
- **11-state run.** The fast C++ tracer `champ/kfirst.cpp` reports the first Kd moment from the halting configuration
  at b = 7, 13, 39 (`champ/kfv11.tsv`). It reproduced the Python tracer's list-length table exactly on the BB(10) set.
  - **Halters (323).** They halt within 631 steps. The best leaves 17, 26, 65 ones at b = 7, 13, 39, which is linear in
    b. The champion's own counts are 11, 17, 43.
  - **Cyclers (649).** None re-enters the Kd shape. 534 are translated cyclers (`champ/tcyc.py`, `tcv11.tsv`) and 115
    are exact cyclers (`champ/cyc.py`, `cycv11.tsv`), all at b = 7, 13, 39.
  - **Deep rebuilds (1530).** The rebuilt list grows linearly in b (digit counts such as 4, 7, 20 or 7, 13, 31). By the
    cap argument of section 3 they never halt. They were not graded one by one, so this rests on the cap argument plus
    the literal growth.
  - **The 6 others.** These rebuild a list that does not grow (`champ/flat11.txt`, `gflat11.tsv`). Their fitted R4 rules
    have no halting class. Odd b maps to `Kd [1] 0 0`, to `Kd [] 0 0`, to `Kd [] 0 (3b+7)/2`, or to `Kd [1,(3b+9)/2] 0 0`,
    and even b maps to the champion's rebuild. So R4 never halts and they never halt. The grader marks one
    NONHALT-PREDICTED and leaves five UNRESOLVED only through precision or event limits.
- **Verdict.** This root gives no record candidate either. Every halting extension leaves at most a linear-in-b
  surplus over the champion.

## Files (`halt_redirect/champ/`)

- **Starts.**
  - `hcfg.py`: halting-configuration builder and literal check.
  - `st_small.txt`: renum starts for b = 7, 9, 11, 13, 23, 39.
  - `st3.txt`: b = 7, 13, 39.
- **Enumerations.** `all9.tsv` and `all10.tsv` print every leaf. `ext9.tsv` and `ext10.tsv` print only the loud leaves.
- **Machine lists.** `m_all9.txt` and `m_all10.txt`.
- **Tracer.** `kcls.py`, output `k9.tsv` and `k10.tsv`.
- **Grader output.** `g9.tsv` and `g10.tsv`.
- **Cycler checks.** `tcyc.py` (output `tc9.tsv`, `tc10.tsv`); `cyc.py` (output `cyc.tsv`).
- **Debug viewer.** `peek.py`.
