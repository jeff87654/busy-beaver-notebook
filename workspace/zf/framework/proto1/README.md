# proto1 — F1: wff stack as a stack of unary registers (measured)

Verdict: **F1 makes the machine larger, not smaller: 406 = 91 framework + 315 DAG, against Wade's 393 = 69 + 324
(+13).** The program does get smaller, but only by 9 DAG states. The new framework op costs 22 states, and 11 of
those are an unavoidable selection chain. The cheapest correct variant I found is the default one (406). Dropping
the depth register gives 401 (still +8), and that variant is **unsound** (see §3). I did not build F1b, because F1
already loses and F1b runs into a layout conflict and loses on its own as well (§6).

## 1. What was built

Files: `TMBuilder.py` (Wade's copy, plus one gadget and one chain property), `zf2s.py` (program), `zf2s.tm` (generated,
Wade format, 406 states). Nothing outside `proto1/` was modified.

### Framework op Q (gadget `1.q`, 9 states; chain `3.<reg>.q`, one state per index 0..k)

Q at chain index k runs after k+1 selector moves, so the tape is `[R_{k+1}] 0 0 [R_k] 0 ... [R_0]`. While it scans for
the selector, it remembers whether the run just left of it, R_{k+1}, is a zero register (`1`):

* **R_{k+1} = 0: MERGE.** It writes `11` into the `00`. R_{k+1} and R_k become one register at index k with value
  R_k+3, and the deeper registers move down one index. The extent of the register file does not change.
* **R_{k+1} != 0: INSERT.** It writes `1` into the second selector cell, then shifts R_k..R_0 right by one cell
  (carry states c0/c1). A new zero register appears at index k+1, and R_{k+1} and everything deeper move up one index.

Why push and pop share one value-dependent op: in Wade's framework every op type needs its own selection chain, with
one state per register index up to the highest index that op is used on. Separate push and pop ops would need two
chains, about 10 + 11 states. A single "push-or-merge" op needs only one chain (11 states).

Why the shift direction is chosen this way: INSERT shifts the **low** registers (R_k..R_0) right into the blank tape.
MERGE changes neither end of the register file. Neither op touches the left end, so the gap never shrinks. The gap
still grows by exactly 1 per decnz, so Wade's IP-space argument (gap is non-decreasing) carries over unchanged. Each
pop adds 3 decnz, which only makes the gap bigger. Max tree depth is 135 (Wade: 136) and max car-run is 9 (unchanged).
The highest register index used goes from 10 to 11, so the chain needs one more cell. The crosscheck measured a minimum
IP-space margin of 4, the same as zf2.tm over the same window.

### Program (zf2s.py)

Registers: 0 prooflist, 1 nextproof, 2 axiomcode, 3-5 param1-3, 6-8 scratch1-3, 9 **depth**, T=10 **top**,
11 **second**, then the deeper stack entries, then the 58 zero runs left by boot. Boot's junk run (value 1) sits at
index 68.

* `pushwff = top+ ; Q(T-1) ; second-`. top is at least 1 when Q runs, so Q INSERTs at index T. The new top is 0, and
  the old top+1 lands at T+1, which the `second-` corrects.
* `pop2 = Q(T) ; top- top- top-`. second is 0 when Q runs, so Q MERGEs, and the three decrements remove the +3.
  pop2 drops a zero second entry.
* `cons = pair(scratch2, second, top) ; move scratch2->top ; pop2`
* `select = if (axiomcode-- > 0) clear second else { clear top; move second->top } ; pop2` (if/else via label)
* `cparam(p)`: in the axiomcode==1 branch, `if_decnz(depth){ move second->scratch1 ; pop2 }`, then `p := scratch1`,
  the same shape as Wade's.
* `main`: decoding is unchanged (Cantor prooflist). The default theorem is now `pushwff ; depth+`.

## 2. Measured counts

All counts use Wade's axiom order unless stated (§4 explains why).

| | Wade zf2.tm | proto1 zf2s.tm |
|---|---|---|
| framework | 69 | **91** |
| DAG | 324 | **315** |
| total | 393 | **406** |

Framework by role (`python fwroles.py X.tm`):

| role | Wade | proto1 | change |
|---|---|---|---|
| boot / 1.inc / 1.sel / 1.decnz / 2.ret / dispatch.1+root | 5/4/6/8/6/2 | same | 0 |
| 3.<reg>.inc + 3.<reg>.decnz | 22 (11 indices) | 24 (12 indices: depth added) | +2 |
| **3.<reg>.q chain** (indices 0..10) | — | **11** | +11 |
| **1.q gadget** | — | **9** | +9 |
| 4.dispatch.2..9 / 6.break / 6.continue | 8/3/5 | 8/3/5 | 0 |

DAG by owner group (`python attrib2.py base|new`, Wade's attrib method generalised; the full lists are in
`*_attrib.txt` and `*_attrib_summary.json`). Only the groups that changed:

| group | Wade | proto1 |
|---|---|---|
| pair (2 instances → 1) | 15 | 9 |
| unpair (3 instances → 1, prooflist only) | 12 | 7 |
| shared move/clear loops | 13 | 9 |
| pushwff | 3 | 2 |
| select | 5 | 7 |
| pop2 (new) | 0 | 3 |
| main: clause DET | 10 | 11 |
| main: default v_0 (+ depth+) | 1 | 2 |
| **net** | | **−9** |

Everything else is identical (if_eq 15, cparam 12, decode 19, clause bodies, glue). The Cantor pair/unpair
instances being removed were already cheap: about 6 states for the second pair and about 5 for both wffstack unpairs.
Wade's DAG shares their loops through hash-consing, so removing them saves little.

Program variants measured at Wade's order (`python zf2s.py '<json>'`):

| variant | fw | DAG | total |
|---|---|---|---|
| default (select if/else, cons move→pop, depth) | 91 | 315 | **406** |
| select = copy-then-pop | 91 | 315 | 406 |
| cons = pop→move | 91 | 315 | 406 |
| cons = Q, clear top, move (no 3×decnz) | 91 | 316 | 407 |
| select = "qdrop" (drop top via Q(T-1) merge) | 91 | 317 | 408 |
| depth.inc before v_0 | 91 | 315 | 406 |
| **no depth register (UNSOUND, see §3)** | 88 | 313 | 401 |

**Break-even:** if Q cost nothing, the total would be 71 + 315 = 386. So Q has to cost fewer than 7 states to break
even, and its chain alone is 11. Under Wade's chain addressing (one chain state per op type per index), F1 cannot
win at all.

## 3. The underflow problem: why the depth register is needed

The original pops from an empty Cantor stack return 0 forever, because 0 = pair(0,0). Nothing stops DET/GEN from
popping below the real entries, since prooflists with arbitrarily many consecutive DET steps get enumerated. With a
register stack, the area below the real entries is boot's register file: 58 zero runs, then a run of **value 1 at
index 68 = wff code 1 = `v0 e. v0`**. Without a guard, the 59th underflowing pop would pull in `v0 e. v0` as a
premise. DET with `(v0 e. v0 -> v0 e. v0)` would then put 1 into top and the machine would halt falsely. So the
no-depth variant (401) is unsound, or at best would need a global "underflow ≤ 57" invariant that I cannot prove.
The depth register costs 5 states: +2 for the inc/decnz index, +1 chain index for Q, +2 DAG.

## 4. Axiom-order hill climb

`hillclimb.py` runs Wade's loop unchanged, at IDLE priority, with a minutes limit. Logs are in `hc_*.log` and the best
order in `hc_*.json`.

* Starting from Wade's optimized order: it converged in 1 pass (8.8 min, about 1100 builds) with **no improvement**,
  so the order stays at 406.
* Starting from the identity order (Wade's exact procedure), limited to 60 min: converged after 2 passes (11.6 min) at **407** with order [15, 1, 0, 11, 12, 13, 14, 16, 17, 3, 5, 7, 8, 9, 10, 6, 2, 18, 4, 19], a local optimum one state worse than Wade's order.

`zf2s.tm` is therefore built with **Wade's axiom order**. That also lets the semantic check compare against the
literal zf2.tm.

## 5. Validation (exactly what was checked)

1. **TM vs RM crosscheck** (`crosscheck_s.py zf2s.tm 30000000`). This is tools/crosscheck.py extended so that the RM
   (`dag.py`, with the Q op added and the IP overflow fixed to give `[]`) holds the **whole** register file: all 201
   runs, initialised from the TM tape at the first op. At every op start it compares the IP and every run.
   Result: **3e7 TM steps, 2031 ops, 0 mismatches** (656 decnz, 803 inc, 14 Q of which 4 merges and 10 inserts,
   558 continue). Minimum gap 7, minimum IP-space margin 4. No `00` appeared inside the register file at any op start.
   The run covers about one main() iteration.
2. **Gadget unit test** (`gadget_test.py zf2s.tm 5000`). The 1.q gadget alone, on random register files (2-13
   registers, values 0-8), with random selector index k and random gap. The test checks the resulting register list
   against the Q model, that the marker is cleared, that the head ends on the last chain one in state 6.break.0, that
   no `00` is left, and that the left end is unchanged. Result: **5000 cases (2062 merges, 2938 inserts), 0 failures.**
3. **Enumerator unchanged** (`semcheck.py ../../ext/turing_machine_explorer/zf2.tm zf2s.tm 2000 3000`). Both RMs run
   symbolically (reduce/symrm.py: Cantor values as structural trees; pair/unpair/if_eq/move loops accelerated; Q added
   for the new RM).
   * (1) **2000 consecutive main() iterations from the boot state** (nextproof reaches 1409). After every iteration it
     compares halt, prooflist, nextproof, axiomcode, param1-3, topwff vs top, the stack contents (orig
     `unpack(wffstack)` vs new `R[11:11+depth]`, trailing zeros stripped), and scratch1-3. It also checks that the new
     RM's tail `R[11+depth:]` still equals boot's `R[11:]`, i.e. nothing was pulled from below.
     Result: **0 mismatches.** Final theorem stack depth 1890; 628110 merges and 630000 inserts executed.
   * (2) **3000 random single iterations** from random states: random wff stacks of length 0-5, sometimes ending in a
     0 entry, sometimes padded in the new RM with 1-3 extra zero entries counted by depth; random junk in axiomcode
     and params; axiom codes 0-22 (every clause); 40% of the stacks set up so that DET fires; p1=1 forced in 10% of
     cases. Stack length 0 covers the underflow path (depth=0). Result: **0 mismatches, 18 halting cases agreed.**

## 6. F1b (`next` op for the proof enumeration): not built, estimate only

The proof sequence would have to live as runs "left of the fixed registers". That is exactly where the F1 stack lives
(indices ≥ T). Popping proof entries from an index below T would shift top/second, and storing them above the stack
needs an unbounded index. So F1 and F1b cannot share one register file without a second addressing mode. F1b alone
(Cantor wff stack kept) would need:

* a `next` gadget for a bijective finite-sequence order, about 15-25 states, plus its chain (≥ 12);
* a pop op for decoding: Q again, 20 states;

That is about +45 framework against at most about −35 DAG (decode 19, prooflist unpair 7, if_not_decnz 9). It would
also change the enumeration order, so Coq L1 would need new work.

## 7. Conclusions for the framework design

* In Wade's framework, any new register op costs **(highest index it is used on + 1) chain states plus its gadget**.
  For ops on the stack top, that index is the number of fixed registers (about 10). That is the real price of F1,
  and it was missing from the IDEAS/NOTES estimate ("+18 fw vs −26 DAG"). Measured: +22 fw vs −9 DAG.
* The Cantor pair/unpair code being replaced was already amortised by hash-consing; per instance it costs only about
  5-7 states.
* F1-style ideas only become attractive if op addressing gets cheaper (F3: a persistent selected register, or
  chain-free gadgets at a fixed tape position). One option I considered: a stack at the left end of the register
  file, next to the gap, needs no chains. But it needs separate inc/decnz gadgets for top and second (about 27
  states), and the stack eats into the IP gap, which would require a new amortised IP-space proof. Estimated at
  94 framework states, worse than this prototype.

## Reproduce

```
python zf2s.py                      # (91, 315, 406) at Wade's order; pass a variant JSON to try the others
python fwroles.py zf2s.tm ; python attrib2.py new ; python attrib2.py base
python gadget_test.py zf2s.tm 5000
python crosscheck_s.py zf2s.tm 30000000          # about 10 min, idle priority
python semcheck.py ../../ext/turing_machine_explorer/zf2.tm zf2s.tm 2000 3000   # about 7 min
python hillclimb.py wade|identity '{}' MAXMIN
```

## 8. Follow-up: stack at the LOW indices (top=0, second=1) is not a valid variant (not built)

Registers are addressed by their position counted from the right: register k is the (k+1)-th run from the right. INSERT at k+1
and MERGE at k change the index of every register **above** the insertion point. That is why the
stack has to sit above all fixed registers (T = number of fixed registers):

* With top = 0 and second = 1, a push (insert at index 0 or 1) would move depth and all fixed registers
  (prooflist, axiomcode, params, scratch) up by one index, and a pop would move them down. Their indices would depend
  on the stack depth. The DAG addresses registers by fixed index (chain length), so the program would read and write
  the wrong registers after the first push. Using the old Cantor encoding here would not help either, because the stack depth is
  unbounded.
* The only way to put the stack low is to make it **not shift** the others. That means a second addressing mode (fixed
  registers counted from the left or gap end, or a stack region outside the register file). Both were costed in §7:
  a left-end stack has no chains but needs about 27 states of left-addressed inc/decnz/push/pop gadgets (about 94 fw), and the
  gap shrinks with the stack. A right-end region gets crushed by sel's rightward creep unless 1.sel is changed.
* So the chain cost of about T+1 = 11 is structural for F1 in Wade's framework. Even with that chain at 0 states, the
  total would be 69 + 2 + 9 (gadget) + 315 = 395 > 393.
