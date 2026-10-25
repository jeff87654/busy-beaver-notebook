# G6 slice of the w+2 search (Opus investigator, 2026-10-09) -- working notes

G6 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI---

## Tools written (this dir)
- stage13.cpp/.exe: stage35g server generalised to <= 16 states (U mask 64-bit). g6lib.py: run_stage/stage/follow
  (ord_run.follow clone, std/big/shrink, any state count) + xstart.  st.py: one literal stage per token config.
- evtrace13.cpp/.exe + ev13.py: tracer (E0 and watched-state reads, per-slot counts with min/max position, PAIR counts
  of consecutive slot reads, LEFTMOST cell).  snap.py (tape snapshots), traj.py (step window), firstleft.py.
- kgram.cpp/.exe + kg.py + kgcmp.py: k-gram (k <= 6) contexts of consecutive slot reads per stage; compares the
  special stages (exhaustion, left event/repack) against normal period stages.
- gs13.py: lazy TNF enumeration of G6 + entry redirect X->K + free K,L,M,J1 through the real-start follower.

## Facts established
1. Reproduced G6 std run with stage13 (27-stage rounds: stage 26 = `7 1^478` -> left -> `1^479|1|19` -> repack
   `6^16 8 1^546 | 1 | 2`).
2. Left event / repack literal anatomy ([1^30|1|19]): the borrow runs off the left end (B1 at 0, F0 at -1), the BASE
   machine unpacks r into (011)^(4r+8) blocks over the cells left of the list, then the E0/I/J conveyor (17 E0 pairs)
   converts them into 6^16 8 at the far left.  Leftmost cell reached = -(8r+26) exactly (r = 19, 79, 139, 259 ->
   -178, -658, -1138, -2098): every left event rewrites ~8R cells LEFT of the list.
3. Growth walk semantics (literal, G6): [X Y 1 P 0 1^n | 1 | r] -> [X-2, 2r-(P-3)/2+1+Y, 1^(n+P+2)] for any token X>=2,
   any Y (Y is absorbed into the new counter token, X is decremented by 2).  With X blank the walk absorbs Y as well:
   [Y 1 P 0 1^n] -> [7 1^(n+..+2Y)] (exhaustion = the same walk with nothing left of the run).  [0 Y ...] (D0 then
   blank) triggers the left-end conveyor; [Z 0 Y ..] with Z >= 2 borrows from Z (Z-3).  [Z P 0 1^n] unpacks Z into ~2Z
   zeros.  [d 2 1^n | R] -> [d-3, 2R+6, 1^n] (D2 refill: d-3 and the 2 refilled from the accumulator).
4. Context uniqueness: NO pair (k=2) and no k-gram up to k=6 of consecutive slot reads occurs in the exhaustion stage,
   the `7 1^n` stage or the left-event/repack stage without also occurring in normal period stages (23 normal configs
   incl. r = 2539 and parked P = 5081; 6 special configs).  => no clone-chain hook of <= 5 cloned states can fire only
   at a round boundary.
5. Survival test (survive.py): every far-left bit pattern F (starts with 1, length <= 8) at gap g = 1..6 left of
   [1^30|1|19] (1530 cases), one literal G6 stage: 36 give G6's standard repack `6^16 8 1^97 | 1 | 2` and ALL of them
   with a clean tape (F erased by the unpack); 1094 change the tokens (F is read as a list digit or merged), 400 W.
   For a far token D(X): gap 1/3 -> X acts as a list digit (no left event); gap 2/6 -> X is MERGED into the new
   counter (X=4: 6^18 8, X=6: 6^18 7^2: u grows by ~X/2, the token is gone); gap 4 -> erased; gap 5 -> junk run
   (`7 1^37` + far, then `2 0 24 6^4 ...`, no G6 rounds).  Nothing survives a left event unchanged.
6. gs13.py bounded enumeration (12 states: entry X->K, K, L, J1 free; 4000-node DFS prefix per entry, all 19 entries):
   see logs/gs13_n2_*.out/.tsv.
   RESULT: 78,745 stage-nodes over the 19 entries (each entry's DFS stopped by its 4,000-node cap, so NOT exhaustive):
   0 halts at stage >= 20; 1,604 halts inside round 1 (stages < 20); 11,079 round-1 token mismatches; 29,476 T and
   32,079 W (junk loops/run-offs); 28 ALIVE through 60 stages (27 are exact G6 emulations: stage 59 =
   `6^12 4 26 1^1039`; 1 is a different non-halting run).
