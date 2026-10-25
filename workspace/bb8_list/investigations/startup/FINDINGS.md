# What sets the 35-digit start? (2026-10-04)

Machine: `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_1LC0RH_1RG1LF` (E0 = `---` in the Coq files).
It reaches Coq's `Kc(2, 0^34; 0; 0)` at step 6397; in Ligocki's notation that is `B(1; [0]*35, 2)` at step 6413.
This note answers where the 34 (or 35) comes from and what would have to change to get more.

## 1. The start-up is one rebuild

Notation (head in G on the blank right of the tape):

    X(x, Z) = 0^inf 1 (01)^x (101)^Z 1 (01)^2 G> 0^inf

For x = 7 and Z >= 2 this is exactly Coq's `Kc(2, 0^(Z-2); 0; 0)`: the digit 2 (run 3*2+1 = 7), Z-2 zero digits, a
zero a-slot and a zero b-slot, each a `1 01` block. `trace_startup.py` (tape at every end-of-tape event,
compressed; `champ35_trace.txt`) and `seed_fn.py` (sequence of X-shaped configurations) show:

    blank --67 steps--> X(2, 1) --finale--> X(7, 0) --rebuild--> X(2, 37) --finale--> X(7, 36) = Kc(2, 0^34; 0; 0)
                        @67                 @197                 @4179                @6397

- **Rebuild.** In X(c, 0) the digit run sits directly against the tail, with no zero digits and no a-slot.
  - Rounds drain it into the tail (`1 (01)^7 1 (01)^2` -> ... -> `11 (01)^16`, steps 197-477).
  - A conversion loop then turns each tail unit into two zero digits (`101101`, steps 754-3982). This is the
    loop that R4's `TLPS` phase runs in the Coq proof.
  - Measured for seeds c = 1..12: **X(c, 0) -> X(2, 4c + 9)**, exactly linear.
- **Finale.** `X(2, Z) -> X(7, Z - 1)` rebuilds the leading digit 2 at the left end (steps 4179-6397). The same
  finale already runs at steps 67-197, turning the prelude's X(2, 1) into the seed X(7, 0).
- **Result.** Z = 4*7 + 9 - 1 = 36 blocks, i.e. **34 zero digits = 4c + 6 with c = 3*2 + 1**: four zero digits per
  unit of the seed run, and the seed is the digit 2 that the finale always writes.

Why it happens only once: R1-R3 keep the list length and always keep the a-slot, so a configuration with Z = 0
never recurs. The used-up list is `Kc(0^n; 0; b)` (Z >= 2), and there the same machinery takes the E0 exit and
halts (Coq's `X4 / TLPS / FIN`).

## 2. The relatives

- **The other two 35-digit machines** run the identical sequence; only the G/H wiring differs:
  - `…_0RG1LD_1RH1LG_1LC0RG`: G and H roles swapped, reaches X(7, 36) at step 6428;
  - `…_1RG1LD_1LC1RH_0LH0RF`: F/H relay, step 6524.
- **The 30-digit rebuilders** (`…_1LC0RH_1RG1RF`, `…_1RG1RH`): their prelude leaves a seed run of 3 and goes
  straight into the rebuild without a first finale (step 63: `1 (01)^3 101101 G>`), so they land on 30 digits.
  - Their R4 rebuild, `K(0^n; 0; b)` -> 12b + n + 7 digits, is the same machinery: 12 digits per counter unit
    = 4 per unit of the 3b+1 run.
- **The BB(7) champion** uses a different start-up shape (state A, `100` blocks) and writes 11 digits.

## 3. No private lever

Transition counts per start-up phase (`python - ` snippet in the session; summary):

| phase | steps | transitions used |
|---|---|---|
| prelude | 1-67 | all 15 defined |
| finale-1 | 68-197 | all 15 defined |
| rebuild | 198-4179 | all 15 defined |
| finale-2 | 4180-6397 | all 15 defined |

R1-R3 also use all 15 (`../rebuilder_nbrs/usage_phases.txt`). No transition belongs to the start-up alone, so no
change to the start-up's constants can avoid changing the digit rules. This is why the exhaustively graded m8
subtree tops out at exactly 35 digits: its 20 CHAMPION machines are the 11-digit and 35-digit start-ups, and its
only other champion-rule machines are the 30-digit rebuilders.

## 4. What would beat 35

- **A finale that writes digit d** gives the seed c = 3d + 1, hence 12d + 10 zero digits and sigma ~ 2↑^(12d+13) 3.
  - d = 2 is this machine (2↑^37).
  - d = 3 would give 2↑^49 and d = 4 would give 2↑^61. Each extra unit of d adds 12 arrows.
- **A steeper rebuild** (more than 4 zero digits per seed unit) or a longer prelude seed are linear gains of the
  same kind.
- **A second empty-context rebuild** before the family starts would give ~4(4c + 9) digits. That needs a finale that
  returns Z to 0, but the finale here only decrements Z.
- **Ackermann-level** growth (a rebuild after counting, halting the second time) is the BB(9)-champion pattern.
  Item 1 found no such machine near the rebuilders (`../rebuilder_nbrs/FINDINGS.md`).

## 5. Search for a longer start near the 35-digit machines

The 35-digit machines' neighbours that keep the champion's first eight transitions all lie in the m8 subtree,
which was graded exhaustively; its longest start is 35 digits. The only new territory is changes to those eight
transitions. Using the four 35-digit machines (`champ35_family.txt`) and the item-1 pipeline:

- 1,024 distinct prefix-changing neighbours (`c35_r1_prefix.tsv`).
- `grade_timeout.py` (full dlscan2, 30 s each): 903 have no digit-list fit, 121 time out (`c35_r1_graded.tsv`).
- `timeout_pass2.py infer` on the 121: their 4,149 candidate templates with a unit of length >= 2 were fitted
  at N = 5000. **0 pass R1-R3** (`c35_r1_timeouts2.tsv`); no template listing timed out.

So **no radius-1 neighbour of any 35-digit machine has a champion-type structure other than the known ones**.
Together with section 3, every single-transition variant either keeps exactly 35 digits or loses the digit rules.

## 6. Not pursued

- **SAT synthesis** of a finale writing digit 3: the bounded-execution encoding is too slow as built. The
  prototype's 4-example rediscovery test (`../sat_synth/champ_fix4.json`, 2.3M clauses, 4 transitions pinned) has
  run about 19 CPU-hours without a result (stopped 2026-10-07 after 55 CPU-hours, still unsolved: `../sat_synth/OUTCOME.md`).
  A start-up example adds hundreds to thousands of steps.
- **The m7 subtree** (first 7 transitions fixed, so E1 is free as well; `../champ12_subtree/m7`, item 2) is the
  systematic search for other start-ups. Its watcher flags any CHAMPION start longer than 35 digits (RECORD-LENGTH).
  None by 15:18 on 2026-10-04 (156,060 holdouts graded).

## Files

- `trace_startup.py MACHINE [MAXSTEP]`: tape at every end-of-tape event, compressed. Output for the 35-digit
  machine: `champ35_trace.txt`.
- `seed_fn.py MACHINE [CMAX]`: the X-sequence from the blank tape and from seeds S(c) = X(c, 0).
- `champ35_family.txt`: the four 35-digit machines (the record machine, its `1LH` sibling, the two relatives).
- `c35_r1_*`: the neighbour search of section 5, using the item-1 pipeline in `../rebuilder_nbrs/`.
