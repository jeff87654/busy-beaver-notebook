# bb8_twoslot -- two-change 8-state neighbourhoods of the three strongest 7-state engines (agent twoslot8, Opus)

Started 2026-10-24.  Bases: (a) BB(7) champion 1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF;
(b) champ_231 1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB and twin champ_232; (c) M8 one-slot changes.
Budget: <= 3 cores, Idle priority.  PIDs in pids.txt (own only).

## Space definition
Parents = base table with <= 2 of the base's 14 slots changed (any value: 32 actions incl. targets in A..H, or halt),
at least one changed slot pointing to H.  H's two slots are lazy (TNF-style): branched over 33 values when first read.
Requires a halt somewhere.  Base (c): M8 with one of its 16 slots changed (no extra state).

## Log
- 13:05 tools: src/tslit.cpp (literal lazy-branching lockstep screener vs the base (write,move) trace), src/batt.cpp
  (jump-rule battery: child vs champion on 3780 small Kt configs, t = 0..6, 10 far contexts, JCL/JR1/exhaustion shapes),
  tools/wtree.py (pkf8t world follower with TNF-lazy branching on H), tools/launch.py (detached Idle launch + PID log).
- 13:09 first full run (BUD 1e6 after divergence) was ~5 h: killed (own PIDs) and split.  Stage 1a = stop at divergence.
- 13:40 stage 1a base (a): 21,896 parents -> 357 S (same (w,d) trace as champion for 1e7 steps), 210,939 X (diverged),
  11,656 H (halt before divergence).  Base (c) M8 one-slot: 480 parents -> 64 S, 394 X, 22 H.
  S-parent shapes: clone-splits (H = copy of D/F/G/A/B/C on one entry), E0 freed by a split (e.g. E0=0LA + F1->H=D-clone,
  halt in the clone's rare slot), guards, and set8 itself (E0 -> xLH/xRH with H lazy).
- pkf8 control (W2 = --B 66 --cls 66 --mod 150): M8 -> zeros 11 817 168 12 753 445x151 446x2, HALT H1 (2 escalations);
  set8 Q5 row E0=0RH,H=---0LC: escalating looper, H0 never read (needk 4e6 is too strict for it: first big CL at 1.2e7).
- 14:20 batt v2 (trace truncated at the jump target; non-jumpable starts skipped): 346/421 S-parents PASS.
  FAIL: 68 at cfg 24 (JR1 m=3 r=0 t=0; F1->H D-clones and C0->H D-clones with D1 changed) -> check every R1 line in their
  world runs for r=0; 7 at cfg 540 (JCL t=1; C0->H D-clone with D1=1Lx) -- all 7 keep E0 = halt, so they halt at the
  champion's exhaustion (t=0 throughout level 0): <= champion.
- 14:25 wtree on 421 S-parents (W2, needk 2e7 300, jumps 400, maxt 1.5e9, maxtops 12 200, wall 90 s, 3 procs) -> runs/wac.tsv
- 15:00 stage 1a base (b): champ_231 21,896 parents -> 465 S, 184,029 X, 9,434 H; champ_232 -> 459 S, 183,486 X, 9,311 H.
  S shapes: C1 (halt) freed + clone-split guard (C1 D1, C1 G0, B0 C1 ...), clone-splits with the halt kept, set of c231ext.
- src/c231f.cpp: champ_231 world follower with the Coq jumps (R1ITER exact; CDP Kc(0^m v Us) 0 B -> Kc(0^(m+1) Us) 0
  iter v (U m) B, m <= B, exact while < 1e9 else representative; --fixed = R = max(RC, m+1) rounded into CLS mod MOD,
  default 39 mod 81 (2R+3 = 0 mod 3^5: the stable residue)).  Controls: champ_231 halts at its exhaustion with ones = 2b+7
  (Coq formula); c231ext family X (C1=0LH,H=---1RB) rebuilds 1^(b-19) forever; 0RH/1LE and 1LH/1LC halt in round 1 (as c231ext).
- src/batt231.cpp + tools/battery231.txt (312 Kc configs, a 0..4, b 0..8): jump battery for champ_231 children.
- 15:35 wtree restarted (resumable, branch regeneration fixed) with maxt 3.5e8, maxtops 4, wall 25 s (rate was 8 rows/min).
  So far: M8 twins (E0=0LH, H=1RD/0RC + H1 halt) reproduce M8's W2 skeleton exactly; C0->H D-clone + D1=0Rx rows
  are E0-avoiding rebuild loops (K' = K + 794, t = 0 constant): arithmetic, non-halting shape.
- m8sweep's wf.exe runs champ_231 (template L,E,P=100,u=11,s=00,d=1d+0,b=1b+0,S=1) but its family-X control shows k=23
  lists (not ~3a); not cross-checked, so I use my c231f for base (b).  Asked m8sweep (no answer yet).
- 17:10 wtree base (a)+(c) DONE: 1637 rows (runs/wac.tsv, rank runs/wac_rank.txt).  Halters with >= 2 escalations: only M8
  (a0231.H01RG) and its 4 known twins (0LH/1RD, 0LH/0RC, 1LH/0RE, 1LH/0RB; c043/c046 in base (c)), all with M8's exact
  W2 skeleton 11 817 168 12 753 445x151 446x2 and ones 3283/3284.  No halter with 1 escalation; 385 halt with 0.
  POSITIVE CONTROL PASSED (M8 rediscovered as a round-3 halter from base (a)); Q5 rows (11 3x2 779x10 781x4 782)
  are non-halting escalators, not flagged.
- haltreach.py (static reachability + bb8_resid backref depth 40) on the 1245 non-halting rows: 956 NOHALT_STATIC,
  189 NOHALT_BACKREF, 100 POSSIBLE (34+15+.. W2-stuck rows with no big clear; arithmetic rebuild loopers with a lazy H1;
  Z-type G-splits with E0 in {0LC (=Z2), 1LF (=Z1), 1RC, 1LC, 1RE, 1LA, 0LA, 0RA, 0LF, 0RB, 1RG}).
- 17:15 deep1: the 100 POSSIBLE rows in W2, maxt 5e9, maxtops 30, wall 150 s -> runs/deep1.tsv
- batt231: 431/465 (231) and 425/459 (232) PASS; every FAIL is at cfg 0 (b = 0, unrealistic: real b >= 5).
- 15:25 (clock check: earlier NOTES times after 14:20 were overestimated by ~2h) deep1 driver died silently at 14:56 (no log, no own kill); restarted (resumable) as deep1b.
- 15:50 BLIND SPOT FIXED: clone-split children may reach the canonical moment in the clone state (H with H0 = B0's move
  for base (a); F/H with E0's move for champ_231), so pkf8t/c231f never jumped there and batt started in the wrong state.
  New: src/pkf8q.cpp (= pkf8t + --qset, state kept across a jump; md5-identical to pkf8t on M8), batt/batt231 test every
  candidate start state X whose 0-slot makes the base Q0's (write,move) and print PASS ... qset=<passing states>; lazy reads
  inside the battery branch over the actions reproducing the base move.  battery231b = battery231 without b < 2 configs
  (unrealistic; every earlier batt231 FAIL was at b = 0).  Battery cap 3e4 gives the same verdicts as 3e5 on a 400-row sample.
- NEW SCOPE for diverged (X) parents: a child that diverges from the base in level 0 but keeps the champion's rules has a
  different START (possibly a bigger first list): batt on all X parents, PASS -> world follower.
- 16:xx lead: console windows from Popen without CREATE_NO_WINDOW; lead patched launch.py/wtree.py (0x40|0x08000000) and stopped pre-patch driver 92276. deep1b ran 99/100 rows.
- WRAP-UP (lead request): REPORT.txt written; X-parent screens and base (b) world trees NOT run. No own PIDs left running.
