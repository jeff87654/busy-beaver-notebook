# 14-state far-run attempt, continuation: live-M enumeration + double clones (2026-10-12)

Continues REPORT_fc14.md (same hit criterion: kD2 must drop at successive round starts and
round counts must scale with K, checked at K = 29 and 71).

## Verdict: NEGATIVE again (screening), including the first double-clone data

Three additions, all negative: an enumeration that starts DFS inside L12f's neighbourhood
with the extra states live, a complete re-follow of every KEEP leaf ever recorded, and the
first two bases (684 variants) of the double-clone sweep at 14 states.

## 1. Live-M enumeration (fc14_1LKz)
`enum12.py --ns 4 --j0 1LK --fix K0=0LM,K1=0RA`: K0 targets M instead of L, so M starts life
as the state L12f's K0 enters, its row branches freely, and N is available after it. This is
the L12f neighbourhood with both spare states live from the first gadget step, which the
1LKx/1LKy runs of REPORT_fc14.md never reached. Stopped at 81.5k nodes (cap 120k):
EAT 2, KEEP 6, NOEND 32. Scan (`fc14_1LKz_scan.txt`): single drops only, mostly whole-run
eats to kD2 = 0 in classes 7/8/9/11, one five-round looper at kD2 = 23 in class 8 with
counter 8 (degenerate). All EAT/NOEND machines re-followed at K = 29, 71
(`fc14_chk_1LKz.txt`): no second drop in any track.

## 2. KEEP leaves closed out
KEEP leaves (first round start with the far untouched) are returned by enum12 without any
follow-up, so REPORT_fc14.md never examined them. All 21 distinct KEEP machines across the
12- and 14-state files (`fc14_keep_machines.txt` plus six new ones from fc14_1LKz) were
followed for six round starts: four loop forever but in classes 8/10 with counters 8/10 and
prefixes ending in digits 37/46 (their ends never go near the far), one has an empty prefix
in class 11 and then dies, one rebuilds a '...2 0 7' buffered prefix in class 12 and then
dies, and the rest restart once only. No transparent class-12 looper exists among them to
serve as a deleter base. The one earlier transparent-looking row (Plen 1, c = 12 in
fc14_1LKx) has prefix [15] and degenerates after two round starts at both K values.
Note: that machine's second round start (stage 96) falls outside enum12's per-round stage
limit (last + 30 + 6c/14 = 83), which is how it became a NOEND; the chk_eat re-follows at
200 stages are what close this gap, and they were run on every file.

## 3. Double-clone sweep started (fc_clone2.py, partial)
`fc_clone2.py` applies the clone construction a second time (state N) on top of fc_clone's
200 looping 13-state machines. Bounded selection: per first-clone slot, the bases with the
minimum, median and maximum plateau kD2 (16 bases; plateaus 2, 15..27, mostly 26); per base,
clone at the originally redirected slot and at M0/M1, varying one N entry over all 56
transitions plus halt (342 variants per base, 5472 planned). Completed so far: the first two
bases (J0 clones with plateaus 2 and 23), 684 variants (`fc_clone2.log`): 292 still make six
class-12 round starts with exactly one drop, 0 make two drops. At roughly 10 min per base
under shared load the remaining 14 bases are about 2.5 core-hours; rerunning the command
restarts from the first base (no resume), so a future run should first add a --skip option
or accept redoing two bases.

## Reading
The pattern is now very consistent across construction styles (lazy TNF at two start tapes,
seeded subtrees, live-spare-state seeding, one and two clone-splits): 14-state gadgets can
eat the far run once, or loop in class 12 behind a rebuilt digit buffer, or leave the far
alone in a class whose end never returns to it, but nothing combines the second and third
behaviours. The cheapest genuinely new experiment left on this route is finishing the
double-clone sweep (the mechanism single and double clones share -- entering the split state
identically each round -- may already explain the outcome, but the data only covers
2 of 16 bases). After that, REPORT.md's estimate stands: a left-end deleter plus a
transparent restart is a deliberate 15+ state design, not a 14-state search away.

## Reproduction (in this dir)
    python enum12.py --out fc14_1LKz.tsv --ns 4 --maxrs 5 --maxnodes 120000 --j0 1LK --fix K0=0LM,K1=0RA
    python fc14_scan.py fc14_1LKz.tsv
    python chk_eat.py fc14_1LKz.tsv 29,71
    python fc_clone2.py            (16 bases x 342 variants; first 2 bases done, no DROP2)

No processes from this continuation are running (enumerations and the clone sweep stopped by
the PIDs in fc14_z_pids.txt; validation runs finished).
