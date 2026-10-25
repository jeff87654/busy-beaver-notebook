# bb8_m8sweep NOTES (agent m8sweep, started 2026-10-24 ~13:00)

Goal: 8-state M8-recipe children (exhaustion slot X of a 7-state f_omega rebuilder redirected into a new state H,
H0/H1 free) that escalate k >= 4 times and then halt (beats M8 = f_w^3(12..13)).

## Tools
- `wf.cpp/.exe` world follower (derived from bb8_resid/tools/zfg7.cpp). Literal TM + JUMPS at K-moments of the base's
  dlscan template: the near token list is cleared (all tokens -> zero digits), accumulator -> representative R
  (R = rc + rk*k, rounded up into class C mod M = the base's tower class). Phase EXACT before the first jump
  (jump only after --slit literal steps), WORLD after (jump at once on big configs).
  Extras vs zfg: O=L templates (mirror), tail forms S1 W^t S2 (M8's (11111100)^t), redirect-slot read counter (--x),
  escalation count (jump with k >= 2 * previous max k, k >= 8), slot bookkeeping (--slots: engine mask = slots used
  between nonzero K-moments, exhaustion mask = slots used after an all-zero K-moment), snapshots, batch mode, and a
  JUMP-LEVEL ACCELERATOR: at each jump the tape is compressed into literals + long periodic runs (period <= 8,
  >= 24 cells); when 4 consecutive jumps have identical structure, identical k and constant run-count deltas, N
  iterations are applied at once (N keeps every shrinking run >= 20 periods). Needed for M8's counter modes.
- `towercls.py` refits the base (reb7 fit7) and evaluates deep clearings with eng7 (Q = 80640): tower residues mod 720.
- `launch.py JOBFILE N`: parallel runner, Idle priority, PIDs -> pids.txt.

## Controls
- 13:18 M8 in world (R0 6, rc 20, rk 1, cls 6 mod 360, tail 11/11111100/1001): HALT H1 after 3 escalations
  (zeros 11, 97, 12, 4374, counter modes 2617^~870 and 2616^~15000 via ACCEL), 1.7e10 literal steps, ~160 s.
  PASS (ctl_m8_v2.txt).
- World variants (ctl/m8_[a-d].txt): a (rc 20, no class) HALT esc 3; c (R0 6, rc 10, cls 6 mod 60) HALT esc 3;
  b (R0 7 odd, rc 10, no class) HALT esc 2 (WRONG CLASS -> early halt: classes matter, use the real tower class);
  d (R0 13, rc 30, rk 2) budget T after 3 escalations.
- Champion tower class (towercls.py): every deep clearing = 32766 mod 80640 -> 366 mod 720 (matches 366 mod 3600).

## Pool
- reb7 runs with growth FOMEGA: 769 seven-state rows. Excluded 53: 18 dl3 bases (bb8_fw1_redirect), 32 hosts2 bases
  (A/B/C + siblings, bb8_fw1_hosts2 fam.py BASES), N2 + mirror, champion (control only), champ_231/232 (c231ext).
  pool.json = 716 bases.
- 13:25 slot detection launched (slots/NNN.txt; wf --slots, 3e8 steps, 8 jumps).
- 13:5x slots v1 done (slots/), v2 with pair bookkeeping (wf2, slots2/): per base the slots used after an all-zero
  K-moment (exhaustion segments; "late" = after the first jump) vs. between nonzero K-moments (engine), and
  (slot, next symbol) pairs. X candidates (xcands.json):
    free = exhaustion-only slots (never used by the engine) + the base's halt slot if reached in the world;
    guard (X,s) = pair seen only in exhaustion segments: X -> H, H copies X's target on 1-s, H(s) free.
  716 bases: 231 with free slots (307 slots) and guards, 158 guards only (615 pairs in all), 327 with neither
  (the exhaustion walk uses exactly the engine's slot/symbol pairs: one new state cannot change the exhaustion
  without changing the engine; structural, see REPORT).
- wf3: --free H0,H1 = TNF-style lazy branching of the new state's slots (only enumerated when read; HALT leaf +
  32 actions); budgets relative to the snapshot; WIDE cap (2^28 cells); world copies per branch.
- towercls over the pool running (towercls_[012].jsonl, 3 cores). Classes are in the towercls template's b coordinate:
  screen.py uses that template.
- Killed my own set8 batch (PID 176816, recorded) to stay within 4 cores; replaced by screen.py control (ctl/scr1).
- LESSON: python heredoc replacements with "\n" inside C string literals produce real newlines -> use Edit.
- 14:00 WORLD SIZE LESSON: the snapshot's first R matters for cost: without --R0 the champion's first jump gets
  R = rc+k = 21 -> rounded 66, the ESC escalation is then at k ~ 1e4 (R^2 ~ 1e8 per re-encoding, budget out);
  with --R0 = class representative (6) M8 halts in ~1.8e9 steps (ctl/m8_c). screen.py/tier.py pass --R0 c (c>=4).
  Minimal worlds (rc 0, cls mod 12 / mod 6) are NOT faithful (ctl/m8_e budget, m8_f halts at esc 2).
- wf4 = wf3 + tape compaction before branching (copies were the bottleneck: 20x) + --escmax.
- towercls classes: non-marker templates agree with reb7's per-round residues; marker templates (P nonempty) differ
  by the staircase (reb7 stores post-staircase values; wf needs the pre-staircase deep-clearing class) -> towercls.
- Tiers: T1 screen.py (lazy H branching, 1e7 from the snapshot) -> promote non-halting leaves with >= 1 escalation
  after the snapshot -> T2 tier.py 3e8 (stop at +6) -> promote >= 2 -> T3 6e9 (stop at +8).
- 14:2x wf5 = wf4 + r1 (rightmost 1) kept as an upper bound with a bounded rescan only at state-Q checks. zfg's exact
  r1 maintenance is quadratic when a machine keeps erasing its rightmost 1 far from the other ones (one leaf: 122 s
  for 1e6 steps -> 0.14 s). Results identical to wf4 on the champion E0=1LH tree (353 leaves). --rcapw (capped world).
- 14:3x wf6 = wf5 + --loop: round signature = sequence of X reads ('x') and non-escalating jumps (log2 bucket of
  k/k_esc) between two escalations; two consecutive identical rounds -> LOOP (structurally periodic world round,
  e.g. the champion's 12R+c rebuild loops: "rsig=x"). Tested: looper 0LH/0LC--- -> LOOP at J3; M8 and 0LH/0LA1LA not.
  Control tier 1 (4 trees, 1252 leaves at 1e7): HALT E1 39, T E1 685, T E2 308, T E3 144, XMAX 76 (M8 is T E2:
  from its snapshot it reaches E3 at +1.3e7 steps and halts at +1.8e9).
- 14:50 towercls done for all 716 (655 one tower class mod 720, 61 two or three classes: each class mod 60 is a
  separate world). Main tier-1 screen launched: screen.py SHARD 3 --out scr (tier-1 budget 3e6, 1e7 for champion
  template), 3 cores; control tier 2 on the 4th.
- 15:1x FIXES before the real run (wf7), all screening restarted from scratch (old dirs ctl/scr1_old_wf4, ctl/t2_old_wf6):
  (1) budget: snapshots taken in the EXACT phase (early small exhaustions; every guard X is read at the very start)
      got --maxt 3e6 < --slit 2e7, so they never reached the world phase (false negatives). Now --maxt/--maxs count
      world-phase steps only; the exact phase is capped by --maxexact (2e8).
  (2) escalation count: k >= 2*max k missed rounds whose world list grows linearly (R = rc + k, so a rebuild of
      length ~R adds only ~rc+rounding per round; real growth is f_w per round). New: escalation iff k > max previous
      k and k >= 0.5 * max previous R (list built from an accumulator). M8 still counts 3 (11, 97, 1494); its counter
      mode (k = 889 < max) is not counted.
  (3) LOOP: round signature = RLE of events (x = X read, j<b> = small jump); LOOP if the last two rounds are identical
      exactly, or the last three identical with log2-bucketed counts (linear-growth rebuild loops, e.g. base 2 guard
      B0: zeros 69,129,189,249 -> LOOP).
  M8 from blank with wf7: HALT H1 esc=3 (1.84e9 literal steps); champion looper 0LH/0LC---: LOOP at J3.
- 16:0x STOPPED at the user's request (token budget). The lead patched launch/screen/sweep/tier.py with
  CREATE_NO_WINDOW (0x08000000 | 0x40): every future Popen of an exe must use those creationflags, never
  shell=True/start/os.startfile/Start-Process. Main tier 1 covered 92/716 bases; tiers 2/3 not run on the pool;
  control tier 3 not run. REPORT.txt written (interim). All own PIDs stopped.
