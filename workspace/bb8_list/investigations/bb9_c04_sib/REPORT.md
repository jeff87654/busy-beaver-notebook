# bb9_c04_sib: C04's neighbourhood (agent c04-sib, 2026-10-18)

The lead wrote this file from the agent's final message (subagents can't write .md). Details: notes.txt (obs1-obs13), runs/.

**Verdict:** no sibling of C04 halts after 3 or more escalations, and none parks an escalation counter. No 2-escalation halter has a larger inner argument than C04. C04 stays the best in its neighbourhood. Status: screening plus model-level evidence, not proofs.

## 1. C04's own gadget (G=0LH1LH, H=1RI---, I=0RI0RF)
- All gadget slots are used before the first exhaustion, so the engine-preserving neighbourhood is E0 = X with H1 as the halt.
- Backref (depth 60) leaves 7 values of E0 for which H1 can be reached:
  - 0RH, 1RH, 1RG halt at the first exhaustion (omega level 1);
  - C01 (0LG) is an f_(w+1)-shape looper: a counter 6R+3 drives fixed-depth clears, and when it runs out the 12R+16 list is cleared and the counter reloaded. The far region is constant, so there is no halt;
  - C02 (1LG) and C03 (0LH) are grow loopers;
  - C04 is the only one that halts after an escalation.
- A literal screen of all 245 one-slot engine mutants found a maximum sigma of 190.

## 2. n1f0 CHAMPION rows (14 rows x 36 E0 = 504 machines, 107 survive backref)
- Beta gadget (C06-C28): the C04-like E0 values (0LC, 0LG, 1LF, 1RD) halt at I1 inside exhaustion #2 in the real class, so sigma ~ f_w(12B) < C04. The rest are early halts, loopers or translated cyclers.
- u=01 rows (35-digit engine, B' >> B) have zero escalations: halts at the first exhaustion, countdowns (about f_40(B') at most), or loopers.

## 3. g07 extension (n1's engine A-H + gadget state I; 288 machines)
- **X1** = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_0RG1LD_1RH1LG_1LC0RG_---0RA (plus 3 twins): an f_(w+1)-shape LOOPER (strong evidence, not proved).
  - Analysed with symx1.py, a symbolic B-form simulator using n1's CLR rule plus probed and affinely fitted events. It assumes a newer accumulator is much larger than all older ones; that puts the key event in the real branch a > 2X, and every linear small world is in the wrong branch.
  - Over 3.5 levels the level map is self-similar: [..,T,3,1^4,Y,2,1,0,X,0,1^n|a] -> [..,T,3,1^2,0,Y,a-2X-3,1^7,0,1^(2X+n-1)|6].
  - Each level leaves one dead frame, the far region (including the parked 1^(2B'+4)) is static, and I0 is never read.
- 2-escalation rows (e.g. ..._---0LD) are loopers with a per-period frame reset.
- Open, probably low: 0RI_I0h_1RC / 1RI_I0h_0RH (an n1-like round, about f_w(2B') per round, below C04 unless the round end re-parks the accumulator), and 1LI_I0h_0RA, 1RI_I0h_0LE, 1RI_I0h_1RE. All stopped on an instantiation artefact. Fix: a large base for the lowest symbol, or symbolic constants.

## Method lessons
- Order-faithful worlds can still pick the wrong branch whenever an event compares a fresh accumulator with 2x an older token. Check event branch conditions before trusting a world.
- Single-event probing plus affine fitting (probe.py, symx1.py) is cheap and generalises to any n1-engine machine.

Tools: pkf6.exe, zfg6.exe, msim*.exe (src/), screen.py, probe.py, symx1.py, lit_x1.py; lists fam504.tsv, keep100.txt, g07ext*.txt.

## Update: X1 PROVED non-halting (2026-10-18)
- backref_s.py (depth 20) gives I0 UNREACHABLE for X1 and its 0RI/1RI twins. The lead checked the invariant against the table:
  - E is entered only via D1 = 1LE, which writes 1 and moves left;
  - E0 = 0RI (or 1RI) moves back onto that 1, so I always reads 1.
- This closes every g07 completion with E0 = 0RI/1RI, including the open rows 0RI_I0h_1RC, 1RI_I0h_0RH, 1RI_I0h_0LE, 1RI_I0h_1RE and 0RI_I0h_0LD.
- Still being checked: the E0 = 1LI twins (I reads the cell left of E; a gap would be needed).
- Halting variants of C01/C02/C03: CLOSED. Only E0 and H1 are exhaustion-only slots, and every outer loop is residue-self-similar.
- E0=1LI twins (I1=0RF, I1=1RA): symbolic event map identical to X1's token for token through 2.5 levels, no halt (strong evidence). The only open row left is 1LI_I0h_0RA (low). Agent stopped; handoff material is in notes.txt obs10-15.
- 1LI twins CLOSED (model-level). Over about 11k E0 reads into level 3 (instrumented msim4.exe), none had a 0 on its left, and the closest approach to the left end was 113 cells. '00' only occurs at the blank left end, which E0 never reaches. The X1 family is closed. Data: runs/sym_tw2.txt, sym_tw3.txt.
