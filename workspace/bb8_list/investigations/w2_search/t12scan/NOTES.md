# t12scan notes (inv Opus, 2026-10-09/10)

Task: scan the 12-state n1 + J0 trees J0 = 0RK (all K0) and J0 = 1RK without inplace's left limit, at the real depth
class, for Tier-1 machines (halt after >= 2 full accumulator-reloaded rounds), and 12-state machines with a free slot.

## Setup
- t12enum.py = inplace/ienum.py with: no left limit (default), n = 329 (35 mod 42), k = 17, R = 19, cut 50, maxrs 3,
  absolute leftmost visit (lo) and leftmost change (mw) recorded per RSIG and leaf, --seed (one K0 subtree per run),
  'hold' file pauses the queue between subtrees.
- queue.sh over queue.txt: 0RK seeds 0RL, 1L*, 1R*, then 0LA..0RK; then 1RK seeds 1R* first, then 0L*, 0R*, 1L*.
  Output trees/<J0>_<K0>.tsv/.log/.done.  (First launch failed on CRLF in queue.txt; fixed.)
- Speed: ~8 nodes/s at n = 329 (16 at n = 77).
- ana.py summarises leaves; val.py = validation battery (std grid, real start, big k = 77/137, affine fit, order test).

## Class correction (lead, 22:55)
- Real k1 = 29 mod 42 and real depth n = 29 mod 42 (h14verify addendum; b0 = 6 follower is wrong mod 49).
- The n = 329 / k = 17 run (0RK_0RL partial, ~1.5k leaves) was stopped and moved to old329/ (not used).
- Restarted the whole queue at k = 29, n = 323.  val.py now uses (k,n) in (29,323) (71,323) (29,365) (71,365) (29,2843)
  (113,2843) (29,1415), big k = 71, 155 at n = 323, fit/order at (29,323); real start b0 = 6 kept as info only.
