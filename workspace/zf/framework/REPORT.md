# Framework-level design study for the "halts iff ZF inconsistent" machine — final report

> Note (lead, 2026-10-11): references to IDEAS.md in sections 1-6 mean **IDEAS_v2.md** (zf-framework2's I1-I10, restored verbatim). The current IDEAS.md is zf-framework's separate list (different numbering), referenced by section 7.

Scope: the machine model / data representation / interpreter / logic representation, as opposed to program-level
work inside Wade's framework (zf-reduce: A361 same `prov`, B354 with equivalent axiom variants, both in the unchanged
69-state framework minus dispatch savings). Files: IDEAS.md (every idea with derivation), NOTES.md (raw facts),
attrib/ (state attribution of zf2.tm), proto1/ (register-stack prototype, full machine), proto2/ (string-gadget
prototype, gadget library). Nothing under zf/coq, zf/ext, zf/reduce was modified.

## 1. Best measured numbers

| machine | framework | DAG | total | status |
|---|---|---|---|---|
| Wade zf2.tm | 69 | 324 | 393 | record |
| zf-reduce A361 / B354 | 66 | 295 / 288 | 361 / 354 | same framework, program-level |
| **proto1 F1** register-stack op (push/merge Q + depth guard), Cantor wffs kept | 91 | 315 | **406** | validated: TM-vs-RM crosscheck 3e7 steps 0 mismatches, 5000 random gadget cases, symbolic enumerator equivalence vs zf2.tm (2000 consecutive + 3000 random main() iterations, 0 mismatches) |
| **proto2 F2** tape-native postfix tokens, string gadgets | engine ~310 (221 measured) | program 45-208 | **~350-518** | gadgets unit-tested (300 random cases each, DET 3000); no whole machine |

No framework-level change found beats the current framework (bar: B354, verified in Coq); both prototypes lose, and the losses are structural
(section 3), not tuning. The honest result of this study is a cost model that explains why.

## 2. Where the 393 states go (measured, attrib/)

* Framework 69 = 38 constant (boot 5, inc/sel/decnz gadgets 18, ret 6, dispatch root 2, break 0/1 2, continue 0-4 5)
  + 22 per register (2 chain states x 11; the chain states are the op leaves, so a leaf costs no extra DAG cell)
  + 9 tree-shape dependent (dispatch.2..9 = longest car-edge run 9 minus 1; break.2).
* DAG 324 = engine 142 (builders 36, Cantor pair/unpair 27, tests 28, select/cparam 17, move loops 13, prooflist
  decode 21) + clauses 178 (exclusive 115: B6a 22, REP 20, INF 19, DET 10, EXT 10, ...; glue shared by 2-14 clauses
  63) + final check 4. 8857 straight-line RM ops -> 470 cells by hash-consing -> 324 by outlining (27 ops/state).
* Rule found by proto1: a new op TYPE costs its gadget plus one chain state per register index up to the highest
  index it is used on. Ops on the stack top (index >= number of fixed registers) cost >= 11 chain states.
* Set theory (EXT REP POW UNI INF) is 56 exclusive states; the FOL engine + logical schemas + framework are the rest.

## 3. Why the alternatives lose (ranked, with estimates; derivations in IDEAS.md)

1. **F1 register-stack op** (I1) — measured +13 (406). DAG saves only 9: the Cantor pair/unpair instances it removes
   were already amortised by hash-consing (5-7 states each). The op costs 9 (gadget) + 11 (chain) + 5 (depth guard,
   required: without it DET/GEN can pop boot's junk run whose value 1 = |v0 e. v0| and halt falsely; the Cantor stack
   is safe because pop of 0 gives 0). Break-even needed the op under 7 states. Placing the stack at low indices is
   impossible (push/pop renumber every register above them). F1b (`next` op enumerating proof sequences): +45 fw vs
   -35 DAG, not built.
2. **F2 tape-native token strings** (I8) — measured engine ~310 against the 142 + 69 it replaces; COPY 56 and DET 69
   dominate because 2-symbol tapes have no cheap markers (a progress marker is a run temporarily zeroed and restored
   token by token). Axiom bodies as push ops cost 0.6 state per token exactly as in Wade's DAG (263 tokens), so the
   program side does not shrink either. Open soundness issue with malformed parameter strings under literal DET.
3. **Program as tape data + interpreter** (I3) — >= 600 by information count: the DAG stores pointers at ~17 bits per
   state; a boot generator yields 1-3 bits/state and the only measured interpreter in this lineage (lambda evaluator,
   NQL/Wade compiler) is 360 states alone. The BLC files in Wade's repo are CatsAreFluffy's BB-lower-bound work,
   not ZF (I4).
4. **Control-flow changes** (I6 `case` op replacing select/cparam: ~0 +-8; I9 cheaper op addressing: negative;
   fixed-height PC / threaded code: NQL measured 737-748 for the same program). Dispatch-shape savings (I5) are
   program-level and zf-reduce already took them (car run 9 -> 7, cap 6 costs +2 cells).
5. **Other calculi** (I7: guess-the-stack, Herbrand/ground resolution, Tarski-Givant relation algebra, single-axiom
   propositional base, giant conjunction) — each either moves cost from building to checking (unpair + if_eq per
   repeated metavariable is dearer than pair), needs string gadgets (as F2), adds registers, or is circular; and all
   except the last two would replace the ~600-line L0/L1 with a far larger completeness/equiconsistency development.

## 4. Soundness and proof work

Both prototypes keep `prov` (Logic.v) unchanged. F1 keeps the RM architecture: Coq cost would have been one new op
in RM.v + a Q-gadget cycle lemma in SimOps/SimRegs (~250 lines; the generic per-cycle framework lemmas and RMEquiv
stay), ZF2Dag/Prog regenerated, and an L1 enumerator with the stack as a list plus the depth-guard invariant. F2 would
replace everything below Logic.v (string RM, gadget lemmas, new L1 over token strings, plus a well-formedness
argument for parameters). Neither is worth doing at these counts.

## 5. Recommendation

Keep Wade's framework. The remaining framework-level headroom is small and known: 38 constant states, 2 per
register (reduce registers, not addressing), and 1 per dispatch level (car-run cap, already at 7). Further gains
are program/logic-level: fewer registers (scratch3 removal measured +3 net by skmendez; parameter-role tricks by
zf-reduce), fewer clauses with equivalent theorem sets (B354/C353 track), and shorter axiom bodies (REP 20, INF 19,
B6a 22 exclusive states are the biggest clause costs; B6a's two if_eq tests are the largest single engine use).
The one framework experiment still unmeasured that could pay is a cheaper decnz/inc gadget family (18 constant
states + 6 ret) hand-optimised for the current layout, worth at most ~5.

## 6. Note on earlier files in this directory

`SM_SPEC.md`, `fwmin/` and `measure/` were left by the earlier (aborted) attempt at this task. SM_SPEC.md is a
spec of the same string-stack idea as F2 (prefix-order wffs, which are prefix-free so DET can match without
delimiters; proto2 reached the same effect with argument-swapped `im` and suffix matching) with an estimate of
~155 framework + ~185 DAG = ~340. proto2's measured gadget library (221 states before the proof odometer, regenerate
and dispatch) shows that framework estimate was optimistic by ~2x; the spec is superseded by proto2/counts.md.

## 7. Addendum (zf-framework, measured after section 6 was written)

* `fwmin/` (RESULTS.md): none of the framework-constant changes saves a state on the zf2 program. Single chain per
  register is impossible with the zf2 DAG (11 inc leaves in cdr position on 7 registers; a leaf hands the framework
  one written bit + an entry state, but inc(P) differs for car/cdr leaves, so three classes per register vs one bit;
  22 chain entries is a lower bound for this leaf mechanism). ret1/ret2 merge >= 0. O(1) dispatch impossible for a
  finite-state left scan (pumping; the marker drifts). Boot -1 (dropping 6.continue.4) needs a 5-state boot with
  gap >= 15 (margin = gap - 15, measured with synthetic tapes); full TNF enumeration of 5-state boots (127M nodes,
  50k-step cap) finds 4472 valid exits but max gap 10. Moore minimisation: no equivalent states among the 393.
* `sm/` + `smfw/` (SM_SPEC.md machine, measured): the ZF program compiles to 228 DAG cells (code tree 34, readers
  21, glue 5, templates 168; max car run 4, depth 31), fully tested on the abstract machine (exhaustive to 2^18
  candidates, planted single-axiom and B7;B3;DET derivations halt exactly on their encodings). The data-side
  primitives as TM fragments, unit-tested against the abstract machine: shared returns 8, INCC 3, DECC 8, NEWT 7,
  NEWP 9, APP1 5, PUSH 32, CHECK 28, RB 43, boot 17 = 160 states for 10 of 14 primitives (shuttle/DUP/DUPT/DET/
  COMMIT unbuilt, ~110 est.), i.e. >= ~420 total, consistent with proto2's conclusion.
* `measure/logic_variants.py`: template variants at Wade's fixed axiom order: B6a distinctor 393 (no gain),
  POW+UNI 398, INF subset form 391 (zf-reduce measured these with search: C353, 355). zf-reduce rejects the B6a
  distinctor form: deriving |- -. A. z z = x in S2 needs the atomic B6 instances being removed (circular without
  Megill's ax-c* axioms), so it is not used.
* IDEAS.md was overwritten at 19:31 by zf-framework's version (cost model, 1a-e, 2a-g, 3, 4, ranked list);
  zf-framework2's I1-I10 text referenced above survives only through this report and NOTES.md/proto*/counts.
