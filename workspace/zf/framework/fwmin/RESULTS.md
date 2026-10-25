# fwmin: framework-level state reductions for Wade's zf2 machine (measured)

Program: Wade's zf2 (imported unchanged from `ext/`), AXIOMORDER = [16,17,3,18,4,7,8,9,11,5,12,13,14,2,15,0,1,6,10,19].
Baseline reproduced byte for byte: `v0_wade.tm` = `base.tm` = zf2.tm (non-comment lines identical), 69 + 324 = 393.

Tools (all in this directory, Python run with `-I`, long jobs via `runlow.py` = reduce/lowprio.py idle priority):

| file | purpose |
|---|---|
| `common.py` | imports tm/TMBuilder/zf2 from ext (read-only), AXIOMORDER, state counter |
| `fwmin.py` | variant generator: copy of `TMBuilder.generate()` with pluggable 5-state boot, no forced `6.continue.4`, optional zf-reduce `ZFP.dechain` cap |
| `xcheck.py` | TM-vs-RM crosscheck (logic of tools/crosscheck.py; P and all 11 registers at every op start; IP-space margin), optional synthetic start tape, first-N `main().0` tape comparison with zf2.tm |
| `leafstat.py` | leaf census (op type x car/cdr position) |
| `dispatchcap.py` | dispatch states vs car-run cap (zf-reduce dechain, imported) |
| `mingap.py` | minimum workable initial gap (synthetic post-boot tapes) |
| `bootenum.c`, `boottnf2.c`, `bootpost.py` | boot searches (Wade-neighbourhood, full TNF), post-check of exit targets |
| `minimize.py` | Moore minimisation of a TM table (zf2.tm: 393 classes, no equivalent states) |

## Summary

| change | framework | total | status |
|---|---|---|---|
| baseline (Wade) | 69 | 393 | crosscheck 2e6 steps: 419 ops, 0 mismatches, min margin 4 |
| 1 single chain per register | (69) | (393) | **impossible** without changing the RM program (proof below); best conceivable gain <= 4 before mark/decoder costs |
| 2 merge 2.ret1/2.ret2 | (69) | (393) | no net saving found (argument below) |
| 3 dispatch cap | 69-(9-c) | see table | dispatch = max(c,2) states; on the zf2 program dechain never pays (cap 8: 394, cap 7: 399) |
| 4 boot into a needed state | (68) | (392) | would save 1 (6.continue.4), but **no 5-state boot with gap >= 15 exists** in the searched space (best gap 10, fails at op 3) |

## 1. Single chain per register: impossible with the fixed RM program

Leaf census of the zf2 DAG (`leafstat.py`):

* every `decnz` leaf is in car position (path bit b = 0): 48 leaves on all 11 registers;
* `inc` leaves occur in car position (b = 0) on all 11 registers **and** in cdr position (b = 1): 11 leaves on
  7 registers (prooflist, nextproof, topwff, axiomcode, scratch1, scratch2, scratch3);
* all break/continue/halt leaves are cdr.

Information argument. A leaf is a DAG transition `(N, b) -> (w, d, X)`. With a binary tape the only things the
framework can learn from it are the written bit w (in the cell holding the last path bit), the direction d and the
entry state X. d = L puts X on the previous path bit, which is arbitrary, so X cannot locate itself (every
attempt to make the chain position-agnostic fails: the chain must count the cells it reads, and a path bit is
indistinguishable from a chain one or a gap zero). So the information is (w, X).

After the op the framework must know (a) the op type t (inc/decnz) for the register file, and (b) the new path.
For inc the new path is inc(P') and depends on b (car: Q1; cdr: inc(Q)0); for decnz b = 0 is known. Hence each
register with a cdr inc has three classes that need different behaviour: (decnz), (inc, b=0), (inc, b=1).
w is a single bit, so one entry state X_k can serve at most two classes of register k, and once the chain is
shared below X_k the class must be recoverable from the tape alone (k is lost in the shared tail; the final
op state sees only the tape). The only tape cell carrying class information is the leaf cell, i.e. 1 bit. So:

* sharing one chain between inc and decnz requires w to encode t (e.g. decnz writes 1 over its b = 0) and then
  b of the inc leaves is lost -> inc(P') cannot be computed for the 11 cdr inc leaves;
* every pre-increment / count-down / delimiter variant ("1 P 0 1^k", writing all k ones in one trip, the
  leaf writing the already-incremented bit, ...) still has to separate the same three classes with the same one
  bit; the count-down only removes the re-walks, it does not create a second bit.
  (Count-based encodings, e.g. decnz r_k entering the chain at index k+11, need a chain of length 22.)

Also: with re-walks (Wade's scheme, k+1 dispatch cycles) any w != b corrupts the next walk, so a flipped
type bit would have to be repaired in every selector cycle by states that already know the type.

Consequence: 22 chain entries are a lower bound for this leaf mechanism with the zf2 DAG (registers with a cdr
inc need two full chains because the second chain also passes through all lower indices). The best conceivable
hybrid (renumber registers so the 7 cdr-inc registers are 0..6, count-down instead of re-walk, decnz flips its
bit, separate 7-state chain for cdr incs) is 11 + 7 = 18 entries plus a decoder and a count-down loop (>= 4
states), i.e. <= 0 net, and it permutes the register file (L3 change) and replaces the selector protocol.
Change 1 becomes possible only if the RM program has no inc leaf in cdr position (an L2 change: about +11 DAG
cells to wrap those leaves, which eats the saving).

## 2. Merging 2.ret1 / 2.ret2

The zero branch is discovered at the selected register; the cells near the IP end (marker) are only written on
the way out (before the outcome is known) and only revisited at the end of the leftward return scan. So the flag
must be carried either in the scan state (Wade: 3 + 3 states) or by a tape pattern that the scan detects. A
detectable flag needs at least a detector + a flagged gap scanner (best design found: ret1, ret1.1, ret1.2
with "1 after exactly 00" -> erase, flagged scanner F2 -> 6.break.1, ret1.3 = gap scanner; 5 states instead of 6)
and the zero case would have to write the flag at the left end of the register file, which is a scan of its own
(more than one state). Variants via break.0 with pre-flipped or extra cells were checked by hand: break.0 on
`Q 0 1^(k+1)` with any extra cell next to the marker yields Q1 (the nonzero result) or a wrong chain, never inc(Q).
Net saving: none found (>= 0).

## 3. Dispatch

`4.dispatch.*` = max(c, 2) states where c = longest run of car edges (consecutive_zeros); zf2: c = 9 -> 9 states.
zf-reduce's `ZFP.dechain(cap)` on the **unchanged zf2 program** (`dispatchcap.py`):

| cap | dispatch | framework | DAG (deepest-first) | total | DAG (top-first) | total |
|---|---|---|---|---|---|---|
| none/9 | 9 | 69 | 324 | 393 | 324 | 393 |
| 8 | 8 | 68 | 326 | 394 | 332 | 400 |
| 7 | 7 | 67 | 332 | 399 | 359 | 426 |
| 6 | 6 | 66 | 343 | 409 | 415 | 481 |
| 5 | 5 | 65 | 373 | 438 | 579 | 644 |
| 4 | 4 | 64 | 450 | 514 | 1214 | 1278 |
| <= 3 | - | - | fails (no inline-safe sequence) | | | |

(In A361 dc7 pays only jointly with the clause-order search.) dechain also changes the DAG (L2).

O(1) dispatch: dispatch scans left over `0^inf 1 P 1^j`. P is a DAG path and its only forbidden pattern found
is 0^(c+1); a finite-state left scan over a zero run needs c+1 states to tell the run inside P from 0^inf
(pumping: with <= c states it enters a cycle on 0s). A double marker does not help because P contains every
short pattern, and the start marker drifts left by one cell per main() iteration (overflow), so no fixed
landmark exists. Mirroring the IP (walk leftwards) moves the same problem to the right end (P vs gap). An O(1)
scheme would need tape marking/zig-zag comparison against a reference run of length > c, which costs more
states than it saves for c = 9 and changes runtime/L3 substantially. Not pursued.

## 4. Boot

6.continue.4 exists only for Wade's boot (the program needs continue.0..3 and break.0..2); generating without
it and with a boot that exits into a needed state gives 68 + 324 = 392.

Required post-boot dispatch tape: `0^inf 1 [head] 0^g (1+0)* 1+`, last 11 runs = `1`, nothing left of the
marker. Minimum workable initial gap measured with synthetic tapes (`mingap.py`, 3e6 steps): g = 15 (margin 0),
16 -> 1, 19 -> 4 (Wade), i.e. min margin = g - 15; g <= 14 fails at op 3.

Searches (exit = (w, d, X) for every framework state X the program needs, plus main().0):

* Wade's boot with only the exit changed: 0 of 234 runs valid (his junk `100 1000^4` needs exactly 4 erasures).
* Wade's boot with <= 3 changed transitions (739k tables, C): no valid boot.
* Full TNF enumeration of 5-state boots (127M tree nodes), 3000-step cap: valid boots exist (exit into
  6.break.2, e.g. `1R1 1R3 1L2 0L3 1R1 0L1 0R0 1R4 1R3 exit`, 11 runs) but the largest gap is 10 < 15.
* Full TNF enumeration, 50000-step cap, tape window +-700 (`boottnf2.c`, 127M nodes, ~70 min idle; Wade's
  own boot is in the output, which shows the enumerator is complete for this window): 157 machines exit with a
  clean `(10)^11` tail; 4472 (machine, exit) pairs give a valid dispatch tape, gap histogram
  {1: 2908, 2: 451, 3: 366, 4: 206, 5: 132, 6: 107, 7: 135, 8: 55, 9: 105, 10: 7}. **Max gap 10**, exits into
  6.break.2 (also 6.break.1/0, 2.ret2.x, chain states). Example `test_gap10.tm` (68 + 324 = 392): crosscheck
  fails at op 3 (IP overruns the register file, margin -6), as predicted by `mingap.py`.
* A 6-state boot entering a needed state would cost as much as Wade's 5 + continue.4: net 0.

Result: no boot saving at 5 states within <= 50k steps / +-700 cells. (Longer-running 5-state boots, like
Wade's 40k-step one, are the only remaining place to look; a 300k-step run is estimated at ~6 h idle.)

## Combined

No change survives: change 1 is impossible with the fixed RM program, change 2 has no net saving, change 3
does not pay on the zf2 program, change 4 finds no boot with enough gap. `zf2_fwmin.tm` is therefore Wade's
framework (69 + 324 = 393, non-comment lines identical to zf2.tm), regenerated by `fwmin.py`:

* crosscheck 2e7 TM steps: 2527 ops, 0 mismatches, min IP-space margin 4, min gap 7;
* first 30 `main().0` tapes identical to zf2.tm.

Where framework savings would need a different L2: (i) no inc leaf in cdr position -> one chain per register
becomes possible (about -11 chain states + mark/decoder, minus the DAG cells for wrapping 11 leaves);
(ii) dispatch via shorter car runs (dechain) only pays jointly with clause-order search, as in A361.
