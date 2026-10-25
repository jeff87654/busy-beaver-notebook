# Framework-level ideas for a smaller "halts iff ZF inconsistent" machine

Scope: the machine model, data representation, interpreter design and logic representation — everything
that changes Wade's 69-state framework or the way the program becomes states. Program-level work inside
Wade's framework (clause dedup, axiom order, cheaper subroutines) is zf-reduce's and is at 354 states
(B354) at the time of writing. All numbers below are for Wade's zf2 program unless stated otherwise;
"measured" means a generated .tm or DAG was counted, "estimate" shows the derivation.

## 0. Cost model (measured, framework/measure/attr.py + fwmin/leafstat.py)

Wade 393 = 69 framework + 324 decision-DAG cells.

Framework 69: boot 5, 1.inc 4, 1.sel 6, 1.decnz 9, 2.ret1 3, 2.ret2 3, 4.dispatch 9 (= longest run of car
edges), 5.root 1, 6.break 3, 6.continue 5 (6.continue.4 only because boot enters it), register chains 22
(11 registers x {inc, decnz}). The RM semantics: DAG cell = 1 state; leaf op = 1 cell + per-register chain
states; a register op on register k costs k+2 dispatch round trips (runtime only).

DAG 324, by deleting parts of the program and recounting (attr.py):

| program part | cells | how measured |
|---|---|---|
| main loop with no axioms (prooflist increment, 4 unpairs + copies, v_0 default, final check) | 62 | axioms = [] |
| + DET + GEN and their support (cparam, pair/unpair/cons, wim/wal, select, if_eq) | +87 = 149 | axioms[:2] |
| + the 18 axiom templates incl. builders (weq/wel/wn/wex/wa, par1-3) and B6a's two if_eq checks | +175 = 324 | full |
| of which B6a alone | 19 | B6a stubbed |

Information view: the 18 templates are 276 ops (counting par_k, v_k, wim, ... as one op each; 235 distinct
suffixes if stored as plain chains). Hash-consing + Wade's infix outlining stores them in ~150 cells, i.e.
~1.8 ops per cell, ~7.5 bits of program per state against a capacity of ~2*(1+1+log2 393) = 21 bits per
state. Templates are 40-45% of the machine and are the floor for any design that keeps "1 cell per op".

Verification cost axis (current Coq architecture, zf/coq): RM semantics + generic simulation proof (L3,
depends on the framework only) + program refinement (L2, depends on the DAG) + logic soundness/completeness
(L0/L1, depends on `prov` and the proof encoding). A framework change costs an L3 re-proof; a program
change costs L2; an encoding/logic change costs L0/L1; a new machine model costs everything.

## 1. Framework constant (Wade's model kept) — MEASURED NEGATIVE except boot

Prototype: framework/fwmin (variant generator for TMBuilder.generate, crosscheck xcheck.py, boot searches).

1a. Single chain per register (22 -> 11, expected -8..-11). Impossible with the fixed zf2 DAG: 11 inc
leaves sit in cdr position (bit 1) on 7 registers; a leaf can only hand the framework one written bit plus
the entry state, and after the op the framework must know both the op type and the leaf's edge bit
(advance = inc(P) differs for car and cdr leaves). Three classes per register, one bit: at most two can
share a chain. Best conceivable hybrid (count-down instead of re-walk, decnz flips its bit, separate chain
for the 7 cdr-inc registers) is 18 entries + decoder/count-down >= 4 = no net gain, and it permutes the
register file (L3). Making all inc leaves car-position costs ~+7..11 DAG cells (wrap as (inc, break 0)):
net <= 0. Verdict: 22 is a lower bound for this leaf mechanism. (fwmin/RESULTS.md section 1.)

1b. Merge 2.ret1/2.ret2 (6 -> 5?): the zero flag is learned at the register and must travel back; a tape
flag needs a detector + flagged scanner (5 states) plus writing the flag at the register side (>= 2):
net >= 0. Negative.

1c. Dispatch: 4.dispatch = max(c, 2) states, c = longest car run (9). zf-reduce's dechain post-pass on the
unchanged zf2 program: cap 8 -> 394, cap 7 -> 399, cap 6 -> 409 (only pays jointly with their clause
search). O(1) dispatch is impossible for a finite-state left scan over 0-runs of length <= c (pumping)
and the IP marker drifts, so no fixed landmark; zig-zag comparison against a reference run costs more than 9.
Negative.

1d. Boot (-1 by not needing 6.continue.4): needs a 5-state boot that exits into a state the program needs
with gap >= 15 (gap g gives IP-space margin g-15; Wade's gives 19). Full TNF enumeration of 5-state boots
(127M nodes, 3000-step cap): valid boots exist but max gap 10. Wade's boot with <= 3 changed transitions:
none. So -1 is not available with 5 boot states; a 6-state boot is a wash. Negative (measured).

1e. Multi-op leaves (a leaf state doing two frequent ops, e.g. "inc; inc"): each costs 1 framework state
and saves (uses-1) cells; the zf2 DAG has few repeated adjacent pairs after hash-consing (the pair is
already one shared cell when it recurs as a suffix). Estimate: -0..-3. Not pursued.

Conclusion: the 69 (66 after zf-reduce's break-level removal) is essentially tight for this program.

## 2. Logic / proof-system changes within the Cantor-integer representation (L0/L1 + L2 cost)

2a. B6a in distinctor form (no side condition): ( -. A. z z = x -> ( -. A. z z = y -> ( ( x = y -> A. z x
= y ) /\ ( x e. y -> A. z x e. y ) ) ) ). Sound for all x, y, z (if z is x or y the antecedent is refutable);
complete because ZF proves -. A. z z = x so the side-conditioned instances follow by two DETs. Removes the two
if_eq checks and four copies (19 cells -> ~10-12 for a 32-op template). Estimate -7..-9 cells. Handed to
zf-reduce (program-level implementation). L0 change: `prov` gets a different B6a (the equivalence of the two
systems is a short lemma: the original B6a instances are derivable; conversely each distinctor instance is
valid, so soundness is unchanged).

2b. POW and UNI merged: E. v1 A. v2 ( ( A. v3 ( v3 e. v2 -> v3 e. v0 ) \/ E. v3 ( v2 e. v3 /\ v3 e. v0 ) )
-> v2 e. v1 ); separation (from REP) recovers both. 26 ops vs 36, one select fewer: -5..-7 cells. Handed to
zf-reduce.

2c. DET by unpairing the major premise instead of rebuilding ( ph -> ps ) and comparing: -5..-7 cells.
Handed to zf-reduce (they may have it).

2d. INF with ( v0 e. v2 /\ A. v1 ( v1 e. v2 -> v1 = v0 ) ) instead of the biconditional: -2..-3 cells.

2e. Proof encoding as a bit string read by the decision tree instead of a Cantor list of 4-tuples: code
tree ~19 cells (= select's 1 cell/axiom), bit reader (halving loop) ~8 + two registers, wff reader
(bit tree + builder calls) ~22 + moving results into param registers ~12 = ~61 cells against the current
unpair x4 + copies + select/cparam ~46. Estimate +10..+15: negative. (Measured in the SM DAG: code tree 34
+ readers 21 = 55 cells, consistent.)

2f. Fewer/shorter logical axioms: Meredith single axiom for propositional logic (21 ops) for B1-B3 (26 ops)
-> -3..-4 cells; equality-free formulation (= defined by extensionality) nets ~0 because B8b/B8c-shaped
Leibniz axioms must stay (-63+28-8+24 ops). Replacing the set theory by an equiconsistent short theory:
Ackermann's A needs a syntactic "V does not occur in phi" check (~20 cells) and its axioms are ~105 ops
vs 139: ~0; NBG (finitely axiomatised) needs pairs and ~30 clauses: much worse. LegionMammal978's PA
machine (372 with one schema instead of the set theory) bounds the whole set-theory contribution at ~60
states, so no theory choice can give more than that.

2g. Other calculi. Herbrand ground instances + brute-force propositional unsatisfiability: removes B1-B4,
DET, GEN (~60 cells) but needs a term table, a clause builder and an assignment enumerator with atom
identification (~60+ cells) and ZF's schemas do not CNF into fixed templates; NBG would be needed: negative.
Tarski–Givant equational set theory: ~10 logical equations (~120 ops, same as B1-B8), an equational
rewrite step with guessed position (~25 cells, same as DET+GEN), longer set-theory equations, heavy
citation: negative. Condensed detachment / unification: the current scheme (explicit parameters) already
is "guess the substitution"; checking unifiers costs more. Lambda calculus / BLC (Wade's lam_*.nql,
loader.blc): a Krivine-style interpreter in Cantor pairs plus loading an n-bit program at ~1 cell per bit
(assemble_blc.py emits one push per bit); a ZF proof checker in BLC is thousands of bits: an order of
magnitude worse. Program-as-data in general: a k-state 2-symbol table carries ~21k bits, the templates
are ~1100 bits, so a data copy would need >= 55 states at perfect density just to exist on the tape, and
no generator approaches that density; the DAG already stores them at 7.5 bits/state with the interpreter
(dispatch) costing 10 states. Negative unless the program shrinks below ~300 bits.

## 3. New machine model: tape-native string-stack machine (SM) — MEASURED NEGATIVE

Spec: framework/SM_SPEC.md. Wffs are token strings in prefix order (runs of 1s, single-0 separated;
theorem/param separators = runs of 1/2 ones), no Cantor pairing, no unary registers; a theorem stack A,
a head/boundary 00, params + work wff + an arity counter c in B; the proof candidate N is a 3-cell-per-bit
binary counter rotated through a sentinel so that reading is non-destructive and the IP gap grows; Wade's
IP/decision-DAG control is reused. Primitives: RB, PUSH v, APP1, NEWP/NEWT, INCC/DECC, DUP k, DUPT, DET,
COMMIT, CHECK. DET works by prefix-freeness of prefix-order wffs (no equality compare of integers); params
are well-formed by construction (pending-operand counter), so no garbage can enter the stack.

Measured (framework/sm, sm-dag agent): the ZF program on SM compiles to **228 DAG cells** (Wade 324):
code tree 34, readers 21, glue 5, templates 168 (106 exclusive + 62 shared); max depth 31 (Wade 136), max
car run 4 (dispatch would be 4 states). Fully tested: templates equal zf2.py's, exhaustive enumeration
to 2^18 candidates never halts and keeps the stack well-formed, planted proofs (single axioms, a B7;B3;DET
derivation) halt exactly on their encodings.

Measured (framework/smfw, sm-fw agent): the data-side primitives as hand-written TM fragments on the exact
layout, unit-tested against sm_abstract: shared returns 8, INCC 3, DECC 8, NEWT 7, NEWP 9, APP1 5, PUSH 32,
CHECK 28, RB 43, boot 17 = **160 states for 10 of 14 primitives**; the shuttle engine (STEP-L/STEP-R),
DUP, DUPT, DET, COMMIT not yet built, estimated ~110 more. Even with a better layout (growth at the free
end: PUSH ~15, RB ~35, shared shuttle) the data side is ~180-200 states, so SM >= 228 + ~15 (IP side) +
~180 = ~420-440 vs 354. Why: a 2-symbol run-length tape has no mark symbol and no parameterised states, so
every "find X, carry a unit, remember a flag" routine is 8-15 states and cannot be shared across its
callers; Wade's unary registers need only inc/decnz (13 states) and push all structure into the DAG where
hash-consing shares it. The DAG saving (-96) is smaller than the framework cost (+110..+150).
Verification: everything would be new (string-level logic, new L1 encoding, string-structure L3).

## 4. Hybrids (one subsystem replaced) — estimates

4a. Tape-native stack primitive for wffstack (push/pop as framework ops) while wffs stay Cantor integers:
removes pushwff/pair/unpair call sites (~12 cells) at ~20 framework states: negative.
4b. Framework copy primitive (copy r_k -> topwff): par_k is already 1 cell per site (subroutine call);
the shared bodies are ~6 cells: negative.
4c. Framework MOVE primitive replacing the ~25 while_decnz move loops (2 cells each): -25 cells for a
~20-state routine with two register operands: ~-5, L3 cost: not worth it.

## 5. Ranked list

| # | idea | measured / estimate | verification cost |
|---|---|---|---|
| 1 | zf-reduce's program-level work (B354) | measured 354 | L2 (+L1 equivalences) |
| 2 | B6a distinctor form (2a) | -7..-9 est. | L0/L1 small + L2 |
| 3 | POW+UNI merge (2b) | -5..-7 est. | L0/L1 small + L2 |
| 4 | DET by unpair (2c) | -5..-7 est. | L2 (L1 if the enumerator spec changes) |
| 5 | INF shortening (2d), Meredith prop. axiom (2f) | -2..-4 each | L0/L1 + L2 |
| 6 | multi-op leaves (1e) | -0..-3 | L3 |
| 7 | boot -1 (1d) | not available with 5 states | — |
| 8 | SM string-stack machine (3) | measured worse (>= ~420) | all layers |
| 9 | bit-string proof encoding in Wade's framework (2e) | +10..+15 | — |
| 10 | single chain / ret merge / O(1) dispatch (1a-c) | impossible or >= 0 | — |
| 11 | lambda calculus, program-as-data, Herbrand/NBG, Tarski–Givant, Ackermann (2f-g) | much worse | — |
