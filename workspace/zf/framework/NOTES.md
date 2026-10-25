# Framework design notes (working file; conclusions saved incrementally)

## 2026-10-10 baseline facts (from DESIGN.md, zf2.nql, README)
- zf2.tm = 69 framework + 324 DAG states = 393. Reduce track (zf-reduce) got 392 by dedup; RESULTS.md table not filled yet.
- Logic: Tarski S2 variant, 17+ axiom codes, proof = list of (ac,p1,p2,p3) Cantor-encoded in one integer.
- wffs = Cantor-paired integers; all arithmetic unary on tape; pair/unpair loops are the cost center.
- Set theory ~60 states (PA machine 372 vs ZF 393 -> actually only ~21 diff? check wiki).
- Register op on reg k costs k+2 dispatch round trips (runtime only, not states).
- Cost model: 1 state per distinct cons cell (hash-consed DAG), framework 69 fixed, ~2 states per register (inc/decnz chain).

## Open questions
- Where do the 324 DAG states go per subroutine? (delegate: dag attribution)
- What did Wade try with lambda calculus (lam_*.nql, bms.blc)? why abandoned?
- skmendez README failures list.

## External facts (2026-10-10)
- skmendez README: RH machine 744->370 in NQL via PC narrowing (1 PC bit ~ 25 states), dedicated copy reg, layout search;
  ZF in NQL: 748 -> 737 only. ZF 393->392 dedup. Failed: axiom-order annealing (<393 none), outlining heuristics,
  remove scratch3 (-2 fw, +5 DAG), narrowing PC (inlining cost). Unimplemented: pair/unpair rewrite (15%), giant axiom conjunction (50%).
- bbchallenge wiki: PA 372 (House, Feb 2026) = Wade's 432 ZF with set theory replaced by adjunction+separation schema
  => set-theory axioms EXT/REP/POW/UNI/INF cost ~60 states in Wade's 432 version. Subtle cardinals 493.
  => in zf2 (393): FOL engine (pair/unpair/select/DET/GEN/B-axioms/main loop) + framework = ~330 states.
- Wade's progression: NQL 588 (Jul 12 2025) -> 549 (Jul 16) -> own compiler 432 (Aug 19) -> 393 (zf2.py).

## Cost-model observations (own, 2026-10-10)
- pair = ~7 cons cells, unpair ~6, if_eq ~8 per INSTANTIATION (register triple). No indirection: each distinct
  register combination is a separate copy. So the cost center is not pair arithmetic per se but the number of
  distinct (subroutine x register-args) instantiations + per-token builder chains.
- Cons cell = 2 pointers ~17 bits; token ~3.5 bits => program-as-DAG is ~4x "wasteful" as data, but a
  data+interpreter design pays generator (~1-3 bits/state) + interpreter; the DAG is already a linked-list
  program in states. Universal-interpreter route loses unless interpreter < ~100 states and program < ~1.5 kbit.
- Suffix sharing is free (cdr = rest of sequence); prefix/subroutine sharing needs a break leaf.
- Candidate framework changes to cost out after attribution:
  F1 stack-of-registers primitive (push/pop run at index k) replacing pair/unpair on wffstack (keeps Cantor wffs).
  F2 token-sequence wffs in the register stack (no Cantor at all) -- needs cursor/second stack; likely new machine model.
  F3 fewer registers via indirect addressing (a "selected register" op that the program moves with sel) to kill
     the k+2 chains and the 2 states/register; cost: more program ops to re-select.
  F4 relation-algebra / Herbrand calculi: verification cost too high; estimate only.
- Program structure (zf2.py): token = pushwff (pair + move) + incs; cons = unpair, move, pair, move.
  Every pair/unpair result lands in scratch and is MOVED back (while_decnz(s, x.inc)) -> many move loops.
  main: 4x (unpair prooflist -> move -> move) to decode (ac,p1,p2,p3). select = move + unpair + move + if + move.
  cparam(p) = pop stack into p if axiomcode==1 (DET/GEN premises).
- Coq layer sizes: framework-specific L3 = Sim.v 670 + SimBase 167 + SimRegs 227 + SimIP 149 + SimDag 301 + SimOps + SimBoot + ZFTM 715 (literal table);
  generic RM.v 175 + RMEquiv.v 789 (reusable for ANY DAG program if the RM op set is kept; new ops => extend RM.v + SimOps/SimRegs);
  program L2 = Prog.v 164 + ProgLib.v 1029 + ZF2Dag.v 1126 (generated); logic L0/L1 = Logic.v + Enum.v + L1*.v ~600 (independent of framework, depends on the abstract enumerator).

## Attribution (agent, files in framework/attrib/, totals verified 69/324)
FW 69: const 38 (boot 5, inc/sel/decnz 18, ret 6, dispatch.1+root 2, break0/1 2, continue0..4 5), per-register 22 (2 x 11),
  shape 9 (dispatch.2..9 = max car-run 9 minus 1; break.2 1).
DAG 324: builders 36 (cons 4, pushwff 3, v_1..4 5, weq..wa 13, par1-3 11); pair 15 / unpair 12 (=27);
  tests 28 (if_eq 15, if_not_decnz 9, if_decnz 4); select 5 + cparam 12; shared move/clear loops 13;
  main preamble 21 (prooflist decode 19); clause-exclusive 115 (B6a 22, REP 20, INF 19, DET 10, EXT 10, B1 6, POW 4, B4 4, ...);
  shared clause glue 63; final check 4.
Leaves: 83 op leaves (35 inc, 48 decnz), 39 control leaves. 8857 expanded ops -> 470 (hash-cons) -> 324 (outlining).
Lambda/BLC files in wade-mtm are CatsAreFluffy's BB-lower-bound work: bare lambda interpreter alone = 360 states. Dead end.

## Design verdict (draft)
- Per-register cost 2 states is near-free; dispatch shape 8 states is the only framework fat (<=5 gain).
- Any register-DAG variant (stack primitive F1, next-sequence counter F1b, case-dispatch) nets ~-10..-25 at best: F1 push/pop gadgets ~+18 fw vs ~-26 DAG; F1b ~+9 fw vs ~-23.
- Only F2 (tape-native token sequences, string gadgets, DAG control) has >10% upside: est 335 +-50; full rewrite incl. Coq.
- Prototype plan: P1 = F1+F1b full machine in a TMBuilder fork (measure+crosscheck); P2 = F2 gadget-cost measurement (encoding + hand TM gadgets, simulated).

## P1 result (proto1/README.md): F1 register-stack = 406 (91 fw + 315 DAG), +13. NEGATIVE.
- Single op Q (push-or-merge, 9 gadget states) + chain 3.<reg>.q 1 state per index up to the highest index used (11 at T=10).
- DAG saves only 9: the removed pair/unpair instances were already shared (~6+5 states).
- Lesson: in Wade's addressing every new op TYPE costs (highest index used + 1) chain states -> put new-op registers at LOW indices.
- Underflow: register stack needs a depth guard (5 states) else boot junk (value 1 = v0 e. v0) can be popped -> false halt.
- Crosscheck 3e7 steps 0 mismatches; gadget unit test 5000 cases; enumerator-equivalence check vs zf2.tm.
- Re-measure with top at index 0 requested (expect ~397).
- zf-reduce status (RESULTS.md): A361 = 66 fw + 295 DAG (same prov), B354 = 66 + 288 (equivalent axiom variants), C353.
  Max car run 7 -> 4.dispatch 6 states (my I5 already partly realized). Framework-level comparisons should quote both 393 and 354.
- SM_SPEC.md / fwmin/ / measure/ = remnants of the earlier aborted attempt (string-stack spec, est. ~340); superseded by proto2 measurements (engine ~310).
