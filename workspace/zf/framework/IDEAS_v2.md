# Framework-level ideas for a smaller "halts iff ZF inconsistent" machine (zf-framework2, restored copy)

Status: final 2026-10-10. This is the zf-framework2 text rewritten verbatim from context after IDEAS.md was
overwritten by the first zf-framework agent (whose version is left untouched). Raw facts in NOTES.md; measured
prototypes in proto1/, proto2/; summary in REPORT.md. Baseline zf2.tm = 393 = 69 framework + 324 DAG; the
verified bar is B354 (66 + 288).

## 0. Cost model of Wade's framework (measured; details framework/attrib/)

Total 393 = 69 framework + 324 DAG.

Framework 69:
* 38 constant: boot 5, register-op gadgets 1.inc 4 / 1.sel 6 / 1.decnz 8, 2.ret 6, dispatch.1+root 2, break.0/1 2, continue.0..4 5.
* 22 per register: 2 chain states (3.<r>.inc, 3.<r>.decnz) x 11 registers. The chain states ARE the leaf states, so an
  op leaf costs no DAG cell of its own beyond the cons cell that points at it.
* 9 shape-dependent: 4.dispatch.2..9 = (longest car-edge run 9) - 1, and break.2.
* RULE (measured in proto1): a new op TYPE costs its gadget + one chain state per register index from 0 up to the
  highest index it is used on. Ops on high-index registers are expensive to add; ops on index 0 cost 1 chain state.

DAG 324 (1 state per hash-consed cons cell; 8857 straight-line RM ops -> 470 cells by hash-consing -> 324 by
longest-first outlining; 83 op leaves, 39 control leaves):
* engine 142: wff builders 36 (cons 4, pushwff 3, v_1..v_4 5, weq/wel/wim/wn/wal/wex/wa 13, par1-3 11),
  Cantor pair 15 + unpair 12, tests 28 (if_eq 15, if_not_decnz 9, if_decnz 4), select 5 + cparam 12,
  shared move/clear loops 13, main preamble 21 (prooflist decode = 4 unpairs + moves 19).
* clauses 178: exclusive 115 (B6a 22, REP 20, INF 19, DET 10, EXT 10, B1 6, POW 4, B4 4, B2/B3/B8a/B8c/UNI 3 each,
  B7/B6c 2, GEN 1, B6b/B8b and duplicates 0) + glue shared by 2-14 clauses 63. Set theory (EXT REP POW UNI INF)
  exclusive = 56, consistent with PA-372 vs ZF-432 (~60).
* final halt check 4.
* Per clause token (postfix builder call) the cost is ~0.5 cell after suffix sharing and outlining; a cons cell
  holds 2 pointers = ~17 bits, a token ~3.5 bits.

Information argument against program-as-data: the DAG already stores the program as a linked list of states at
~17 bits/state. A tape-resident program needs a boot generator (~1-3 bits/state in practice) plus an interpreter;
the only universal interpreter measured in this family (CatsAreFluffy's lambda evaluator in NQL, Wade's compiler)
is 360 states by itself. Program-as-data loses unless interpreter < ~100 states and program < ~1 kbit.

## 1. Ideas

### I1. Register-stack primitive replacing the Cantor wffstack (F1) — MEASURED: 406 (+13). Negative.
Design: one framework op Q(k) = "insert a zero register at k, or merge if the deeper neighbour is 0" (9 gadget
states) + chain 3.<r>.q (1 per index up to the stack top, 11 at top=10) + a depth register (5 states, needed: without
it DET/GEN can pop below the stack into boot's junk, whose run of value 1 = |v0 e. v0| would cause a false halt).
Program: pushwff = inc+Q+dec, cons = pair(scratch, second, top)+move+pop2, select/cparam via pop2.
Measured (proto1/zf2s.tm, Wade's axiom order; hill-climb found nothing better): framework 91, DAG 315.
DAG only -9 because the replaced pair/unpair instances were already shared (5-7 states each). Break-even would need
the new op to cost < 7 states; its chain alone is 11. Placing the stack at indices 0/1 is invalid: push/pop renumber
every register above the insertion point, so the fixed-index DAG would address the wrong registers (proto1 README §8);
even with a free chain the best case is 69+2+9+315 = 395.
Validation: TM-vs-RM crosscheck 3e7 steps 0 mismatches; 5000 random gadget cases; symbolic enumerator-equivalence
vs zf2.tm over 2000 consecutive main() iterations + 3000 random iterations, 0 mismatches.
Verification cost had it won: RM.v + SimOps/SimRegs gain an op (new per-cycle gadget lemma, ~250 lines), L2 regenerated,
L1 abstract enumerator changes (stack as list instead of Cantor integer) but Logic.v/prov unchanged.

### I2. Framework `next` op enumerating proof sequences directly (F1b) — estimate: worse (+45 fw vs -35 DAG).
Needs a bijective finite-sequence successor gadget (~15-25) + chain (>=12) + a pop op (~20); saves prooflist decode 19,
one unpair 7, if_not_decnz 9. Layout conflict with F1 (both want the region left of the fixed registers). Not built.
Would also change the enumeration order -> L1 rework.

### I3. Program as tape data + small universal interpreter — estimate: >= 600. Negative.
Information content: 324 cells x 2 pointers x 8.6 bits = 5.6 kbit as raw pointers; even compressed to a ~1.5 kbit
token/bytecode program, a boot generator at the practical 1-3 bits/state costs 500-1500 states, plus an interpreter
(a register-machine bytecode interpreter with unary registers needs addressing by value = loops over the register
file; >= 60 states; the only measured interpreter in this lineage, CatsAreFluffy's lambda evaluator, is 360).
Only the DAG-as-states representation stores pointers at ~17 bits/state. No prototype.

### I4. Lambda calculus / BLC (Wade's repo lam_*.nql, bms.blc) — dead end, not ZF-related.
Those files are CatsAreFluffy's 2024 BB-lower-bound work (BMS, Loader's number): a call-by-value closure evaluator
over Cantor-paired unary registers, programs emitted as straight-line NQL pushes (not tape data). Bare interpreter
497 -> 360 states with Wade's compiler; lambda BMS 584 vs hand-written BMS 507. A ZF enumerator in lambda terms
would add several hundred states on top of 360.

### I5. Dispatch shape: cap the longest car-edge run — estimate: -1 to -5, program-level knob.
4.dispatch.2..9 = 8 states exist only because the IP may contain up to 9 consecutive zeros (car run 9). Restricting
nesting depth of first-elements to Z costs cells where the program is restructured; each unit of Z saves one state.
Handed to zf-reduce (TMBuilder knob): already at car run 7 (cap 6 costs +2 cells, cap 5 +20). Also: TMBuilder lacks
the NQL "combine_states" merge (states only ever entered reading 0 merged with states only ever entered reading 1);
zf-reduce measured it: saves 0 on TMBuilder output (only 1.inc is single-symbol, no partner).

### I6. `case r` op: jump into a cdr-chain by the unary value of a register (replaces select/cparam) — estimate: ~0.
Op in car position sets P := prefix 1 1^r (append ones, then flip the preceding 0); clauses hang at prefix 1 1^k 0 and
end with break 2, which strips the k ones for free, so the exit is uniform in k. Saves select 5, part of cparam ~8,
axiomcode clear 2 and one select call per clause (~20 cells) but costs a (body, break2) cell per clause (+20), the
gadget (~10) and its chain (index of axiomcode + 1). Net ~0 +-8; the current "every clause builds, select discards"
trick is already the cheap solution. Not built.

### I7. Different calculi (minimize engine, let the proof do the work) — estimates, none built.
* Guess-the-stack (enumerate wff sequences, CHECK each is an axiom instance): instance-check = one unpair per node
  instead of one pair per node plus if_eq (8 cells) per repeated metavariable: worse than building (+30..60).
* Herbrand ground instances + ground resolution: needs set-of-literal union/compare on tape (string gadgets as in
  F2) plus Skolemized REP schema; engine no smaller than F2's and the Coq side (completeness of ground resolution,
  Skolemization of schemas) is far larger than the current L0/L1. Rejected.
* Tarski-Givant variable-free relation algebra: removes GEN, B4, B6a-c, B7, B8a-c, cparam for variables (~60 states),
  but equational proof steps need subterm replacement (context substitution into Cantor trees = recursion, or one
  congruence rule per operator argument ~6 rules x ~6 tokens) and the set-theory equations are very long; the
  equiconsistency argument is book-length. Rejected.
* Single-axiom propositional base (Meredith, 21 tokens vs B1-B3's 24) needs 5 parameters: +2 registers (+4 fw),
  longer decode (+6); net positive. Rejected.
* Merging schemas into one giant conjunction needs conjunction elimination, which needs the propositional axioms
  that are inside the conjunction: circular with DET/GEN only. Rejected.

### I7 (numbers). Estimates against the verified bar 354 (B354 = 66 fw + 288 DAG). None is credibly below 330.
| calculus | engine delta vs Wade (142 DAG + 69 fw) | clause delta vs 178 | total estimate | why |
|---|---|---|---|---|
| guess-the-stack (check instead of build) | +30..+60 (one unpair per node like pair, plus if_eq ~8 per repeated metavariable: ~12 repeats) | 0 | ~420-450 | checking costs more than building |
| Herbrand + ground resolution | needs F2's string gadgets (measured engine ~310) + clause-set union/compare (~+40) | axioms as Skolemized clause sets, REP schema instances guessed: ~150-200 | ~500+ | no cheap tape representation of literal sets |
| Tarski-Givant relation algebra | -60 (no GEN/B4/B6/B7/B8/variable params) +congruence/transitivity rules ~6x6 tokens ~+25 DAG, subterm replacement via explicit contexts needs recursion (+40) or one rule per argument position (included) | set-theory equations (QRA + translated ZF) several hundred tokens: +100..+200 | ~450-550 | axioms far longer; equiconsistency argument book-length |
| Meredith single propositional axiom (5 params) | +4 fw (2 registers) +6 decode | -3 tokens (~-2) | ~+8 | more parameters |
| giant conjunction of schemas | circular: elimination needs the propositional axioms inside it | - | n/a | rejected |
| NBG finite axiomatization (no REP schema) | 0 (parameters still needed for logical schemas) | class axioms ~15 x ~15 tokens: +100 | ~450 | more tokens than REP's 20 states |
Prototype worth building: none. The only candidate with a credible route below 354 remains program-level work in
the existing framework (register count, clause bodies REP/INF/B6a, equivalent axiom variants).

### I8. Tape-native postfix token sequences with string gadgets (F2) — MEASURED engine ~310; total 350-518. Negative.
proto2/: token t = run 1^(t+1) with single-0 separators; regions IP | gap | persistent proof P | working copy X |
stack S. Gadgets written as TM fragments and tested against Python references (300 random cases each, DET 3000):
NEWTOK 8 + UNIT 9 (push-token c = NEWTOK + c UNITs), front-decnz 6, DELWFF 7, POP 21, COPY p_i 56 (35 shared core),
DET 69 (90 with the POP scan it reuses), GEN 27, shared walk-back 18: library 221 distinct states. Plus boot 9,
proof odometer ~26 (partly built), regenerate-X ~25 (not built), B6a core 14 (built), step dispatch ~15: engine ~310.
Program: 263 literal tokens + 23 parameter copies in 16 axiom bodies (REP 56, INF 45, EXT/UNI 23, B6a 21, POW 19):
(A) bodies as push ops at 0.6 state/op + ~36 control = ~208 -> ~518 total; (B) bodies as tape templates plus an
instantiate gadget (~40) -> ~350-395. Both lose to A361/B354. Encoding tricks that saved states: binder stored as
`ph x al` (GEN = append), implication stored argument-swapped so DET matches a SUFFIX (no hole to close).
Open soundness issue: parameters are arbitrary strings; concatenating a malformed ph can yield a well-formed wff with
an unintended reading, and junk entries can combine under literal DET — needs a well-formedness check (+30-40) or
syntax-building steps. Verification cost: everything below Logic.v is new (string RM, gadget lemmas, new L1).

### I9. Cheaper op addressing (F3) — rejected by analysis.
Per-register cost is 2 chain states (one per op type) because the DAG leaf state must identify (register, op). A
single chain per register would need the op type carried on the tape or in the IP; the leaf transition cannot
record which symbol it read, and a marker written elsewhere must be found by the gadget (>= +4) while the leaf would
still need to differ by op (so no saving). A persistent "selected register" with explicit sel ops in the program
replaces 22 chain states by sel leaves (cells) at every register change: the program switches registers almost every
op (~8800 expanded ops, hundreds of cells after sharing). Negative.

### I10. SM string-stack machine (sm/, from the first attempt): DAG measured 228 cells; framework estimate 230-270 -> total ~460-500. Negative.
Framework derivation (proto2 measured costs in brackets): Wade IP mechanics 19 (dispatch root 2, dispatch cap 4 -> 3,
break levels 4, continue levels 4, chain-trip gadget 6) + walk-out/back chains 18 [18] + leaf entry states 22
(RB, PUSH x9 values, APP1, NEWP, NEWT, INCC, DECC, DUP x3, DUPT, DET, COMMIT, CHECK) + PUSH 17 [NEWTOK 8 + UNIT 9]
+ APP1 4 + NEWP/NEWT 6 + INCC/DECC 6 + DUP 30-45 [COPY 56] + DUPT 3 + DET 45-65 [69, 90 with scan] + COMMIT 10
+ CHECK 13 + RB/END odometer and N rotation 30 [odometer 26 + regenerate 25] + boot 8 = 231-266.
To beat 354 the framework would need < 126 states, but IP mechanics + entry states + walk chains alone are ~59 and
PUSH + DET alone measured 86 in proto2. SM's own spec estimate (155) already gives 383 > 354.
Plus of SM over proto2: typed wff reader makes parameters well-formed by construction (closes proto2's soundness gap).
Main risk if built anyway: DET/DUP gadget cost on a 2-symbol tape (measured 56-90 each) and the N odometer.
