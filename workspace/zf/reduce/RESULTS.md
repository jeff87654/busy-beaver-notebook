# Reducing the ZF machine below 393 states — results

Working directory: `zf/reduce/`. Nothing in `zf/coq/` or `zf/ext/` was modified. The candidate machines
are in `reduce/cand/` (`NAME.tm`, the config `NAME.json`, the abstract enumerator in Enum.v syntax
`NAME.enum.txt`, and the validation log `NAME.val`).

## Summary

| track | best | formal system `prov` | what has to be re-proved |
|---|---|---|---|
| A | **361** (`cand/A361.tm`) | **unchanged** (same Logic.v) | L1: Enum.v clause table and axiomorder (generated), plus bookkeeping in the compile lemma. L2: regenerate ZF2Dag.v; ProgLib lemmas for the rewritten subroutines; new loop-head invariant "param1..3 = 0". L3: constants only (see below) |
| B | **354** (`cand/B354.tm`) | the same theorems: three ZF axioms are replaced by logically equivalent variants | Track A, plus either changing the Logic.v axiom literals (reviewer compares them with zf2.nql and checks the equivalence on paper) or keeping Logic.v and proving in L1 that the variants and the originals derive each other (pure logic: commutation of /\ under A./E., symmetry of =, one alpha-variant) |
| C | **353** (`cand/C353.tm`) | the same theorems, but one direction of the equivalence is set theory | Track B, plus trusting a new axiom PU (POW and UNI merged), or formalizing S ⊢ PU (pairing and union in the Hilbert system, which is a lot of work) |

Recommendation: **A361**. It cuts 32 states (8%) and leaves the trusted definition of `prov` untouched.
B354 saves 7 more states for a small, purely logical equivalence argument. C353 saves one more state
beyond that and is not worth its cost.

All candidates keep Wade's framework (boot, register operations, dispatch, IP arithmetic) and his
compiler (TMBuilder.py: decision DAG with longest-first common-subsequence outlining). What changes is
the program (`zfp.py`). Candidates with `dc7` also get a semantics-preserving post-pass on the outlined
sequences. Every candidate still has 11 registers. Every candidate came out of a search over clause
order, per-clause parameter roles and, for B/C, axiom variants.

## Candidates

| file | states | framework+DAG | track | changes (cumulative) | TM-vs-RM crosscheck: ops / mismatches | semantic test: trials / mismatches | max car run / max depth / max break / IP prefix ops |
|---|---|---|---|---|---|---|---|
| `ext/.../zf2.tm` (Wade) | 393 | 69+324 | - | original (rebuilt byte for byte by `build.py`) | 2527 / 0 | 1500 / 0 | 9 / 136 / 2 / 358 |
| `cand/dedup392.tm` | **392** | 69+323 | A | duplicate B6b/B8b clauses removed; Wade's order hill-climb | 2527 / 0 | 2000 / 0 | 9 / 145 / 2 / 386 |
| `cand/perm388.tm` | **388** | 69+319 | A | + per-clause parameter-role permutations; joint order+perm search | 2448 / 0 | 2000 / 0 | 9 / 138 / 2 / 269 |
| `cand/T385.tm` | **385** | 69+316 | A | + cpord, detS3 (DET-only rewrites) | 2527 / 0 | 1000 / 0 | 9 / 136 / 2 / 358 |
| `cand/A361.tm` | **361** | 66+295 | A | + b6aD, tagall, cp3, sel3, push2, ifeq2, dc7 | 5610 / 0 (1e8 TM steps) | 2000 / 0 | 7 / 125 / 1 / 310 |
| `cand/B354.tm` | **354** | 66+288 | B | + commuted /\ <-> = in EXT, INF, REP; INF alpha-variant | 5622 / 0 (1e8 TM steps) | 2000 / 0 | 7 / 123 / 1 / 294 |
| `cand/C353.tm` | **353** | 67+286 | C | + POW, UNI merged into PU (bound variables renamed); no dc7 | 6154 / 0 (1e8 TM steps) | 2000 / 0 | 8 / 120 / 1 / 237 |

Every candidate also passes `symrm.py` (each accelerated node checked against plain op-by-op execution:
0 mismatches). "IP prefix ops" is the number of RM ops until gap ≥ depth+12+3 holds forever, with the
gap modelled as 16 + #decnz (`ipbound.py`; this convention gives 358 on zf2.tm where the Coq proof uses
347). The minimum margin inside the prefix is 1 for every machine, as it is for zf2.tm. The measured
min IP-space margin in the TM crosscheck is 4 for all of them, as for zf2.tm.

### Final clause orders (positions 1..N; parameter roles in `NAME.enum.txt`)

* A361: REP B1 POW B7 GEN DET B3 UNI B6c B8c B4 EXT B6b B8a INF B8b B2 B6a
* B354: EXT DET B7 INF REP GEN B3 B6b B8c B8a B4 UNI B1 B6c POW B8b B2 B6a
* C353: INF B8b EXT B3 DET B8a B4 REP PU B7 B8c B1 B2 B6c B6b GEN B6a

### Track B / C axioms (all other axioms as in Logic.v)

B354:
* EXT  `( A. v2 ( ( v2 e. v0 -> v2 e. v1 ) /\ ( v2 e. v1 -> v2 e. v0 ) ) -> v1 = v0 )`
* REP  `( A. v3 E. v1 A. v2 ( A. v1 ph -> v1 = v2 ) -> E. v1 A. v2 ( ( E. v3 ( v3 e. v0 /\ A. v1 ph ) -> v2 e. v1 ) /\ ( v2 e. v1 -> E. v3 ( v3 e. v0 /\ A. v1 ph ) ) ) )`
* INF  `E. v2 ( v1 e. v2 /\ A. v1 ( v1 e. v2 -> E. v0 ( A. v2 ( ( v2 e. v0 -> v1 = v2 ) /\ ( v1 = v2 -> v2 e. v0 ) ) /\ v0 e. v2 ) ) )`
  This is INF with v0→v1, v1→v2, v2→v0, the inner /\ swapped and v2 = v1 flipped. Its free variable
  (the seed) is now v1 instead of v0.

C353 (EXT, REP, INF as commuted variants, see `cand/C353.enum.txt`):
* PU   `E. v3 A. v1 ( ( -. A. v2 ( v2 e. v1 -> v2 e. v0 ) -> E. v2 ( v1 e. v2 /\ v2 e. v0 ) ) -> v1 e. v3 )`
  (= `E. y A. z ( ( z C_ v0 \/ z e. U. v0 ) -> z e. y )`; it replaces both POW and UNI)

## Changes: soundness and verification delta

The theorem in every case is `halts tm c0 <-> prov (v0 e. v0)`. The question is (i) whether the
enumerator still pushes exactly the theorems of `prov` (L1), and (ii) whether the DAG still implements
the enumerator (L2).

### Enumerator level (prov unchanged; L1 only)

* **dedup** (−1). zf2.py lists B6b and B8b twice. A clause is a map (p1,p2,p3) ↦ axiom instance. A
  duplicate clause only gives a second axiom code that produces exactly the same instances. Removing it
  leaves the set of pushable theorems unchanged, since any proof using the second code can use the
  first. L1: an 18-entry clause table, and compile uses the remaining code.
* **perm** (−4). Per clause, the parameter registers that play the scheme's roles are permuted. For
  example, B1 builds ((p3→p2)→((p2→p1)→(p3→p1))). As (p1,p2,p3) ranges over N³ so does any permutation
  of it, so each clause's instance set is unchanged. For DET/GEN, the register that receives a popped
  premise moves with its role. For B6a, the distinctness test follows the z role. L1: the clause_k
  definitions are permuted (generated, see `NAME.enum.txt`), and compile picks the permuted parameters.
* **order**. The clause order is searched; Enum.v is already parametric in `axiomorder`. There are two
  constraints. DET/GEN may not be last (Wade's constraint, because the last clause also catches every
  ac > N). With b6aD, B6a must come after every clause that reads a parameter, so only EXT/POW/UNI/INF/PU
  may follow it. `zfp.valid` enforces both.

### Program level (same abstract `enum_step`; L2 only unless noted)

* **cpord** (−4). DET copies ps into topwff with loop body [tw.inc, s1.inc] instead of
  [s1.inc, tw.inc]. The effect is identical, and the loop becomes par_a's own loop, so it is shared.
* **detS3** (−1). DET's second pop (the major premise) goes straight into scratch3, instead of into p_b
  and then a copy p_b → scratch3. When DET is selected, the comparison is the same and scratch3 is
  zeroed by if_eq. When it is not selected, nothing is popped, s3 = 0, and the result is discarded by
  select. (Originally the major premise stayed in p_b for later clauses, but those are never selected in
  that iteration.) L2: DET's clause_post no longer writes p_b.
* **b6aD** (≈ −9). The B6a side-condition test is now destructive: z→s1,s3; x→s2;
  if_eq(s2,s3){tw:=0}; s1→s3; y→s2; if_eq(s2,s3){tw:=0}. Its effect on topwff is unchanged (zeroed iff
  z=x or z=y), with the side effect param1..3 := 0. B6a runs in every iteration and comes after all
  parameter readers, so the params are 0 at every loop head. main() therefore no longer zeroes them
  before decoding. L2: the loop-head relation in Prog.v (currently "params arbitrary") must say
  "param1..3 = 0"; the initial state is all zeros.
* **tagall** (−2..3). The wff constructors tag without a stack round trip:
  tag_k = [s1:=tw; tw:=k; tw:=(s1 . tw)], using cons's pair(s2,s1,tw). weq/wel/wim/wal =
  [cons, tag_0/1/2/4] and wn = tag_3. The codes are the same. This also removes v_4.
* **cp3** (−1). cparam(scratch3) skips the zeroing loop, because scratch3 is 0 by the scratch
  invariant.
* **sel3** (−3). New select: if ac>0 (decrement), pop and drop the previous wff; if ac=0, drop the built
  wff and pop the previous one into topwff through scratch1, sharing the unpair(s1,s2,ws) instance. The
  effect equals Wade's select, and the unpair(topwff,scratch2,wffstack) instance disappears.
* **push2** (−5). pushwff = [s1:=tw; tw:=ws; s2:=(s1 . tw); ws:=s2], through the pair(s2,s1,tw)
  instance. The effect is the same, and the second pair instance pair(s1,tw,ws) disappears.
* **ifeq2** (−1, a framework state). In if_eq, the "in1 > in2" exit now zeroes in1 and sets in2 := 1,
  then falls into the shared "in2 ≠ 0" exit (zero in2, skip the body). The effect is the same, and since
  no break of level 2 remains, framework state 6.break.2 is not generated. L3: break levels ≤ 1.
* **dc7** (−1, a framework state). A post-pass (`ZFP.dechain`) runs after outlining. It inlines
  sequences whose breaks and continues all stay inside them, along car chains, until no IP has more than
  7 consecutive zeros, which removes one 4.dispatch state. Each inline step is checked: it is only done
  when no break/continue in the sequence's subtree targets or escapes it, so it preserves semantics
  (sequential composition is associative). L3: "max 9 consecutive car edges" becomes 7.

L3 constants of A361 (ZFTM.v / Sim*.v): 11 registers (unchanged), max car run 7 (was 9; 4.dispatch.1..7),
break ≤ 1 (was 2), continue ≤ 4 (unchanged), max walk depth 125 (was 136, so the IP bound goes from 149
to 138 cells). The `ip_space` prefix has to be recomputed (≈310 ops by our convention, vs 358 for zf2.tm).
The framework is literally Wade's, minus the states the generator omits. 66 framework states = 69 −
4.dispatch.8 − 4.dispatch.9 − 6.break.2.

### Track B (theorem set identical)

* **flips**: inside EXT, INF and REP, the operands of /\ and <-> and of = are swapped. **INF
  alpha-variant**: bound and free variables renamed (the universal closures are alphabetic variants).
  In each case the new axiom and the old one derive each other in pure logic: propositional commutation
  under A./E. via GEN+B4 (L1 already has `ex_mono`), symmetry of = from B8a and `x = x` (which L1
  already derives), and instantiation/generalization for the alpha-variant. So the two systems prove
  exactly the same theorems. Renamings inside the REP scheme were excluded on purpose, because variable
  capture in `ph` makes that argument delicate.

### Track C

* **PU**: POW and UNI are replaced by the PU axiom shown above. POW and UNI follow from PU in pure logic
  (P → (¬P → U) and U → (¬P → U), monotone under A./E.). PU follows from POW, UNI and REP in ZF − Reg −
  AC: take P(v0) and ∪v0, form the pair {P(v0), ∪v0} by replacement on P(P(∅)), and take its union. The
  theorem sets are again equal, but this direction is a set-theoretic derivation.

## Opposite tape-liveness merge (Wade's NQL `combine_states`): measured, saves 0

The idea is to merge a state that is only ever entered reading 0 with one only ever entered reading 1.
In NQL it was worth about 17 states. On TMBuilder output it saves nothing:

* **Decision-DAG states.** A node is entered reading 0 when its car starts, and reading 1 when its car has
  finished normally (the IP bit flips). `liveness.py` computes the possible exits of every car
  statically. On zf2.tm, A361, B354 and C353, **no** DAG node has a car that can never finish normally,
  so every DAG state is entered with both symbols.
* **Framework states.** Wade already applied this merge by hand in TMBuilder's framework (its comments:
  "with a 1 on the tape 1.decnz is actually 1.decnz.f", "1.sel ... is actually 1.decnz.j"). The only
  remaining single-symbol state is `1.inc` (entered only on 0; its 1-row is already absent, and L3 shows
  it is unreachable). None of the framework scanning states is entered only on 1, so 1.inc has no
  partner. A 5*10^7-step run also found no state entered only on 1 (`rowuse.py`).

Column for the table: combine_states saving = 0 for every candidate.

## Validation method (designed once, run on every candidate: `validate.sh` / `finalize.sh`)

1. `crosscheck.py` (tools/crosscheck.py) compares the TM against the atomic RM. At every op start it
   checks the IP path and all registers. It runs 2·10⁷ TM steps (≈2000–2500 ops), and 10⁸ steps
   (5600–6200 ops) for the three best. It also reports the IP-space margin.
2. `symrm.py` is a symbolic structured interpreter of the DAG. Wff codes are astronomically large (one
   main() iteration builds INF, REP, ...), so concrete unary execution of a single iteration is
   impossible, which is why the crosscheck only covers the start of the first iteration. In symrm, values
   are Python ints or Cantor-pair trees with an offset. pair/unpair/if_eq entry nodes and straight-line
   move loops are executed abstractly; everything else runs op by op with RM.v's structured semantics.
   Its self-test compares every accelerated node against plain execution on random small values.
3. `semtest.py` is the semantic test. It runs one full main() iteration of the candidate's DAG from
   random states and compares four things against an independent Python port of `Enum.v`'s
   `enum_step`: (pl, np, tw, ws), the halting decision, scratch = 0, and params = 0 where that is an
   invariant. The reference's clause formulas are written by hand from Logic.v / zf2.nql, not from the
   program tokens. Variant axioms are evaluated from `forms.py` trees, whose default trees are checked to
   equal the hand-written formulas. The random states cover every axiom code 0..N+2, small colliding
   parameters (the B6a side condition), wff-valued parameters, matching and non-matching DET premises,
   ps = 1 (the machine must halt; ≈30 halting cases per 2000 trials), and the prooflist = 0 branch.
   Sensitivity check: a machine with the B6a test deliberately removed fails it.
4. `ipbound.py` computes the RM-level IP-space prefix described above.

What is not validated by execution: TM-level behaviour beyond the first ~6000 ops. That part is covered
generically by L3, because the compile scheme and framework are Wade's. Also, the logical-equivalence
arguments of Tracks B and C are on paper only.

## Things tried that did not help

* **Conjoining axioms.** Each clause costs one `select` element; a conjunction costs one `wa` element
  per merge, so conjunction alone saves nothing. Merging B8b and B8c (common antecedent) into one clause:
  360 at best, against 354 for the same search without it.
* **Dropping axioms.** Only the duplicated clauses can be dropped. EXT was kept on purpose: equiconsistency
  of ZF without extensionality depends on how replacement is formulated (Gandy's interpretation uses
  collection; Scott 1961 shows that the replacement form behaves differently). With REP in this sharp
  form that argument is not safe, so it was not pursued. POW, UNI, INF and REP are independent.
* **INF with the singleton written `A. w ( w e. z -> w = x ) /\ x e. z`** (a pure-logic equivalent):
  355, no better than the plain flips.
* **A cheaper outliner.** Random tie-breaking was worse on average than Wade's choice. A dechain cap of 6
  instead of 7 was worse.
* **Small rewrites:** fused cons+tag builders (+3), DET popping the major premise first (+1), GEN's
  premise via scratch3 (+4), a B6a test by saturating subtraction (+10), and a select in the last clause
  that zeroes axiomcode. None helped.
* **Removing scratch3** needs extra if_eq instances, which cost more than the 2 framework states it saves.
* **Search.** Annealing / late-acceptance and iterated local search over order × parameter roles ×
  axiom variants (several CPU-hours at idle priority) plateaued at 361 / 354 / 353.

## Files

* `zfp.py`: the program (clause table, `PERM`, `VMAP`/`FLIPS`, `OPT` flags listed above, dechain,
  outliner speedup that leaves its output unchanged). `forms.py`: axiom trees and variants.
  `zf2.py, TMBuilder.py, tm.py, tmdb.py`: Wade's files (unmodified copies). `build.py` reproduces zf2.tm.
* `climbp.py`, `anneal.py`, `ils.py`, `vmscan.py`: searches (IDLE priority through `lowprio.py`).
  `runs/`: search logs and configs.
* `mkcand.py`, `finalize.sh`, `validate.sh`, `crosscheck.py`, `dag.py`, `tmsim.py`, `symrm.py`,
  `semtest.py`, `ipbound.py`, `constants.py`, `chains.py`, `enumspec.py`, `showseq.py`, `table.py`.
* For L2, `tools/gen_coq_dag.py cand/NAME.tm OUT.v` generates the ZF2Dag.v for any candidate (it is
  generic in the .tm).
