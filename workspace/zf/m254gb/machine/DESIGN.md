# m254gb machine: zfc_254 + ¬Goldbach (halts iff ZFC ⊢ GC)

Goal: a TM that halts iff ZFC + NG is inconsistent, i.e. iff ZFC ⊢ GC. NG is the closed sentence
"some even m ≥ 4 is not a sum of two primes". This is the verified 254 program (`../../m254`,
frozen) with one change. Its AX bundle

    bundle(a,b,c) = (C ∧ G') ∧ (V∈ ∧ V=)            (zfc_254, 281 states on Wade's route)

becomes

    bundle'(a,b,c) = bundle(a,b,c) ∧ NG'              (gated exactly as before)

NG' is a fixed closed sentence. It uses only the constant variable labels 0..3 (`v_0`..`v_3`) and
never the AX parameters a, b, c. Everything else is unchanged: rows ρ1..ρ8, GEN, the gate
`c≠a ∧ c≠b`, MP, DROP, NIP and the coding. Compiled with Wade's TMBuilder (the 281-state route of
m254tg).

**Result: 399 states** (`m254gb_wade.tm`, source `source_gb.py`), against the 281 baseline (+118).
NOT frozen. NG' has 410 RPN tokens (the base bundle has 93).
`sha256(m254gb_wade.tm) = dbff2885c482a6857f3627ca08d794a0679b125a2facd01809e43656036b6a11`, `sha256(source_gb.py) = 41a73af159d55bb1934a9b734dccccd83966d833d92b543f53a85e7d44fcf5e7`.

## 1. The chosen NG'

### 1.1 Idea

Numbers are finite von Neumann ordinals n. Arithmetic is cardinal arithmetic of subsets of n.
There are no pairs and no recursion:
* a sum is a 2-block partition of n;
* a product is a *grid*: two orthogonal partitions R (rows) and C (columns) of a set X, where every
  row meets every column in exactly one point, so |X| = |R|·|C|;
* "n is a finite ordinal" is "every subset of n has a least and a strict-maximal element, and n is
  transitive". It is enforced on the blocks of all 2-partitions, which are all the subsets of n.

The text is self-similar on purpose. Wade's builder factors repeated token runs, and cost is
roughly one state per *unique* token. So a single partition block `Part` serves three uses: the
Goldbach split, the grid rows and the grid columns. The grid text serves Ev and GF. Rebinding (`∃n∈F`
inside GF, `∀F((F=R ∨ F=C) → …)` inside the grid) makes the copies textually identical.

### 1.2 Named reading

```
NG' = ∃n [ Ev(n) ∧ GF(n) ]

Part(n,F)   = ∀x∈n ∃r∈F ( x∈r ∧ ∀s∈F (x∈s → s=r) )  ∧  ∀r∈F ∀u∈r u∈n      F partitions n (∅ allowed)
NT(n,F)     = ∀r∈F ∃x∈n ¬x∈r                                               no block is all of n
Grid(n;R,C) = ∀F ( (F=R ∨ F=C) → (Part(n,F) ∧ NT(n,F)) )
              ∧ ∀r∈R ∀c∈C ∃x∈r ( x∈c ∧ ∀y∈r (y∈c → y=x) )                 rows ⟂ columns
Two(F)      = ∃c∈F ∃d∈F ∀e∈F (e=c ∨ e=d)                                   1 ≤ |F| ≤ 2
Ev(n)       = ∃R ∃C ( Grid(n;R,C) ∧ ∃F (F=R ∧ Two(F)) )                    n even, n ≥ 4
GF(n)       = ∀F ( (Part(n,F) ∧ Two(F)) →
                   ( ∃n∈F ( ∃R ∃C Grid(n;R,C)  ∨  ∃y ∀x∈n x=y )            some block composite or ≤ 1
                     ∧ ∀Y∈F ∀z∈Y ( ∀w∈z w∈n                                (A = n gives: n transitive)
                                   ∧ ∃m∈Y ∃M∈Y ∀k∈Y ((m∈k ∨ m=k) ∧ ¬M∈k) ) ) )   least + strict max
```
Bounded quantifiers: `∀x∈s A` = `∀x(x∈s → A)` and `∃x∈s A` = `∃x(x∈s ∧ A)`. Inside GF, `∃n∈F`
rebinds n to the chosen block. The outer n is not used below that binder. `∀w∈z w∈n` sits outside
it and refers to the outer n.

Meaning (in ZF; see 5.1): n is a finite ordinal, |n| = 2·|C| with |C| ≥ 2, and every 2-partition
{A, n∖A} has a block of size ≤ 1 or of composite size. That is: n is even, n ≥ 4, and n is not a sum of
two primes.

### 1.3 Labelled reading (what the machine pushes)

Labels: n = v0, R = v1, C = v2, F = v3. The bound helpers reuse v0..v3 wherever no capture
occurs; `ngdsl.check` verifies every occurrence. Connectives as in zfc_254: `A∧B = ¬(A→¬B)`,
`∃x A = ¬∀x¬A`, `A∨B = ¬A→B`, `¬A = A→F`, F = code 1 = Rel(0,0).
```
∃v0 (∃v1 ∃v2 ((∀v3 ((v3=v1 ∨ v3=v2) → ((∀v1 (v1∈v0 → ∃v0 (v0∈v3 ∧ (v1∈v0 ∧ ∀v2 (v2∈v3 → (v1∈v2 → v2=v0))))) ∧
    ∀v1 (v1∈v3 → ∀v2 (v2∈v1 → v2∈v0))) ∧ ∀v1 (v1∈v3 → ∃v2 (v2∈v0 ∧ ¬v2∈v1)))) ∧ ∀v0 (v0∈v1 → ∀v1 (v1∈v2 → ∃v2
    (v2∈v0 ∧ (v2∈v1 ∧ ∀v3 (v3∈v0 → (v3∈v1 → v3=v2))))))) ∧ ∃v3 (v3=v1 ∧ ∃v0 (v0∈v3 ∧ ∃v1 (v1∈v3 ∧ ∀v2 (v2∈v3 →
    (v2=v0 ∨ v2=v1)))))) ∧ ∀v3 (((∀v1 (v1∈v0 → ∃v0 (v0∈v3 ∧ (v1∈v0 ∧ ∀v2 (v2∈v3 → (v1∈v2 → v2=v0))))) ∧ ∀v1
    (v1∈v3 → ∀v2 (v2∈v1 → v2∈v0))) ∧ ∃v0 (v0∈v3 ∧ ∃v1 (v1∈v3 ∧ ∀v2 (v2∈v3 → (v2=v0 ∨ v2=v1))))) → (∃v0 (v0∈v3
    ∧ (∃v1 ∃v2 (∀v3 ((v3=v1 ∨ v3=v2) → ((∀v1 (v1∈v0 → ∃v0 (v0∈v3 ∧ (v1∈v0 ∧ ∀v2 (v2∈v3 → (v1∈v2 → v2=v0))))) ∧
    ∀v1 (v1∈v3 → ∀v2 (v2∈v1 → v2∈v0))) ∧ ∀v1 (v1∈v3 → ∃v2 (v2∈v0 ∧ ¬v2∈v1)))) ∧ ∀v0 (v0∈v1 → ∀v1 (v1∈v2 → ∃v2
    (v2∈v0 ∧ (v2∈v1 ∧ ∀v3 (v3∈v0 → (v3∈v1 → v3=v2))))))) ∨ ∃v3 ∀v2 (v2∈v0 → v2=v3))) ∧ ∀v1 (v1∈v3 → ∀v2 (v2∈v1
    → (∀v1 (v1∈v2 → v1∈v0) ∧ ∃v0 (v0∈v1 ∧ ∃v2 (v2∈v1 ∧ ∀v3 (v3∈v1 → ((v0∈v3 ∨ v0=v3) ∧ ¬v2∈v3))))))))))
```
`extract_rpn.py` prints the same formula from the compiled source (conjunct 4; see 4).

### 1.4 De Bruijn reading (library order; ⊥ for the code-1 literal after IR normalisation)
```
∃[(∃[∃[((∀[(($0=$2 ∨ $0=$1) → ((∀[($0∈$4 → ∃[($0∈$2 ∧ ($1∈$0 ∧ ∀[($0∈$3 → ($2∈$0 → $0=$1))]))])] ∧ ∀[($0∈$1 →
    ∀[($0∈$1 → $0∈$5)])]) ∧ ∀[($0∈$1 → ∃[($0∈$5 ∧ ¬$0∈$1)])]))] ∧ ∀[($0∈$2 → ∀[($0∈$2 → ∃[($0∈$2 ∧ ($0∈$1 ∧
    ∀[($0∈$3 → ($0∈$2 → $0=$1))]))])])]) ∧ ∃[($0=$2 ∧ ∃[($0∈$1 ∧ ∃[($0∈$2 ∧ ∀[($0∈$3 → ($0=$2 ∨
    $0=$1))])])])])]] ∧ ∀[(((∀[($0∈$2 → ∃[($0∈$2 ∧ ($1∈$0 ∧ ∀[($0∈$3 → ($2∈$0 → $0=$1))]))])] ∧ ∀[($0∈$1 →
    ∀[($0∈$1 → $0∈$3)])]) ∧ ∃[($0∈$1 ∧ ∃[($0∈$2 ∧ ∀[($0∈$3 → ($0=$2 ∨ $0=$1))])])]) → (∃[($0∈$1 ∧
    (∃[∃[(∀[(($0=$2 ∨ $0=$1) → ((∀[($0∈$4 → ∃[($0∈$2 ∧ ($1∈$0 ∧ ∀[($0∈$3 → ($2∈$0 → $0=$1))]))])] ∧ ∀[($0∈$1 →
    ∀[($0∈$1 → $0∈$5)])]) ∧ ∀[($0∈$1 → ∃[($0∈$5 ∧ ¬$0∈$1)])]))] ∧ ∀[($0∈$2 → ∀[($0∈$2 → ∃[($0∈$2 ∧ ($0∈$1 ∧
    ∀[($0∈$3 → ($0∈$2 → $0=$1))]))])])])]] ∨ ∃[∀[($0∈$2 → $0=$1)]]))] ∧ ∀[($0∈$1 → ∀[($0∈$1 → (∀[($0∈$1 →
    $0∈$4)] ∧ ∃[($0∈$2 ∧ ∃[($0∈$3 ∧ ∀[($0∈$4 → (($2∈$0 ∨ $2=$0) ∧ ¬$1∈$0))])])]))])]))])]
```

## 2. Variants measured (Wade TMBuilder, states incl. framework; baseline 281)

| family | formula (summary) | NG' tokens | states | note |
|---|---|---:|---:|---|
| orig | zfc_254 bundle (reproduced) | 0 | 281 | baseline |
| A (`cands.py`) | Nat = Tr ∧ Trich ∧ ∀X⊆n(strict min ∧ strict max); Ev = Comp(n) with "rows have ≤ 2 points"; GF over explicit splits (A,B), X=A∨X=B; grid = two halves + swap | 732 | 445 | sound; greedy labels |
| B/C/D (`cands2-4.py`) | as A, one ∃! per point/row, NT as "∀r∃x¬x∈r", Two unbounded | 486–606 | 430–435 | **unsound**: Ev(0) and GF(0) both hold (0×0 grid, split ∅+∅), so NG' is ZF-provable. Rejected (found by hand; the model checker confirms that ψ(0) holds for family D) |
| E (`cands5.py`) | one Part block reused (split = 2-partition family), swap for columns, Two bounded | 544 | 402 | hill-climb over labels/orders |
| **F (`cands6.py`), chosen** | E + `∀F((F=R∨F=C)→Half)` instead of the swap; merged LM | 410 | **399** | SA over 26 role labels × 20 order switches |
| F, textbook Nat (`lmx=1`) | Tr(n) ∧ Trich(n) at top; LM = strict min ∧ strict max | 444 | 403 | slightly easier ZF adequacy |
| F, NG' placed elsewhere | before the bundle, inside V-part, inside C∧G' | same | same ±0 | placement is irrelevant |
| F, labels shifted to 1..4 | label 0 never bound (the F literals then mention a free v0) | same | +2 | NG' with label 0 is literally closed, so label 0 is kept |
| control | NG' := ∃v1 v1∈v1 | 5 | 287 | decode check, section 4 |

Cost breakdown of the chosen formula (ablations, cost only): Grid + Part + Two (Ev alone) +86;
GF on top of Ev +32, of which LM +20 and Small +8; Ev on top of GF +2 (it reuses the grid text).
So the composite certificate is the dominant cost.

Notes.
* Cost ≈ 1 state per unique token. For example, `Small` (13 tokens) alone costs +15, and a reused
  block costs about one state per reference. The search space is labels (which equal sub-strings
  share), conjunct orders, and the ∃! forms. Logs are in `runs/` (`hc_*.jsonl`, `sa_*.jsonl`). Runs
  under `runs/invalid_Frole/` are void: a generator bug rendered the role named F as falsity.
* Degenerate cases (n ≤ 3, 0×0 grids, empty blocks) are what broke families B–D. The chosen
  formula is therefore checked by brute force: `mc_chosen.py` (ordinals 0..3, all n ∈ V_5 with
  |n| ≤ 2) and `mc_grid.py` (all partition pairs for |X| ≤ 6). Family A also passes ψ(0..3) = false
  (`mc_famA.py`).
* Not pursued, because they are estimated to be more expensive: ternary Goldbach (3-splits plus n ≥ 6
  cost more than parity), Kuratowski-pair bijections, ω-recursion graphs of +/×, and a
  Goldbach-checker run as a set.

## 3. Collision and coding notes

* **NG' is closed and constant.** It contains no par1/par2/par3 token and no c+1. So for every gate-open
  AX, `D(bundle' a b c) = BW a b c (D c) ∧ NG'_wff`, with NG'_wff independent of a, b, c. All m254
  collision cases (a = b, etc.) concern only the BW part and are unchanged. The gate (c ≠ a, b →
  else 0) is unchanged. NG' is conjoined outside every a/b/c binder.
* **Label reuse inside NG'.** Labels 0..3 are rebound many times (for example, v0 = n, then a row
  witness, then a min element). `ngdsl.check` resolves every atom occurrence to its intended binder.
  The labelled reading in 1.3 shows the result, and `extract_rpn.py` reproduces it from the compiled
  source.
* **F = Rel(0,0) literals.** NG' is entirely inside `∃v0`, so every F produced by wn/wa/wex/∨ inside
  NG' is captured: it reads `x∈x` for the current v0. The existing IR normalisation of m254-logic
  (`x∈x ↔ ⊥` under binders of v0, used for a = 0 and for tg296's f) applies unchanged. All later
  arguments (L, quotient) are done after normalisation. With labels 1..4 instead (+2 states), the
  F literals would mention a free v0, so IR normalisation is needed either way.
* **No 0/τ collapse.** No subformula of NG' has code 0 (checked on the decoded RPN). The
  bundle's top code is still `wa(…)`, an Imp code ≡ 0 mod 4, so the NIP argument holds unchanged.
* **Completeness (machine side).** NG' is recovered as the second conjunct of any gate-open bundle
  instance, for example (a,b,c) = (1,2,3), by ∧-elimination (L-derivable).

## 4. Validation (all in this directory)

| check | result |
|---|---|
| `ng_final.py` builds `source_gb.py` / `m254gb_wade.tm` from `chosen.json`; `gen.py orig` reproduces the 281 baseline | 399 / 281 |
| hand-written `spec.NG` (independent transcription of 1.3) vs the symbolic RPN of the compiled source (`validate.check_rpn`, random a,b,c incl. gate/c+1/a=b/0 collisions) | 0 mismatches |
| mutation test (`mutation.py`): each of the 40 atom positions of `spec.NG` swapped or shifted | all 40 mutants caught (each on 20/20 samples) |
| `validate.py 20000` (`validate.log`): helper closed forms, 5,000 unaccelerated and 20,000 accelerated main runs vs `spec.enum_step` (AX codes with NG' fingerprinted) | ALL OK: helpers 0, RPN-vs-spec 0, 5,000 unaccelerated 0, 20,000 accelerated 0 mismatches (6,232 AX, 295 halts) |
| `compiler.py 300` (`runs/compiler.log`): completeness-macro contracts through `spec.enum_step` | 5,700 contracts, 0 failures |
| small-model semantics (`mc_chosen.py`): Small/Comp/Ev/GF on ordinals 0..3 = [1100]/[1000]/[0000]/[1100]; the NG' body is false for all 137 sets n ∈ V_5 with |n| ≤ 2 | ALL OK |
| grid semantics (`mc_grid.py 6`): for X = 0..6 and all pairs of set partitions (also with an ∅ block), Grid ⟺ (|r∩c| = 1 ∀r,c; |R|,|C| ≥ 2) or X = R = C = ∅; Ev shapes: 4 → 2×2, 6 → 2×3 | 0 mismatches |
| `extract_rpn.py` on `source_gb.py` | conjunct 4 = the formula of 1.3 (no code-0 subformula; labels {0,1,2,3}) |
| positive control (`ng_final.py control`, `source_gbctl.py`, 287 states): NG' := `∃v1 v1∈v1` (refuted by IR) | `extract_rpn` decodes conjunct 4 as `E.v1 R(v1,v1)` |
| rebuild determinism (`ng_final.py` twice) | identical .tm |

## 5. Proof sketches for the chosen NG'

Notation. "ZFc" means the library ZF (no Regularity), "ZFR" means ZFc + Reg, and "S0/SIR" are the m254 settheory theories. A *2-partition* of n is
a set F with Part(n,F) ∧ Two(F): F = {A, B}, where A ∪ B = n and A ∩ B = ∅ (A = B is impossible
unless n = ∅; ∅ ∈ F is allowed).

### 5.0 The theories involved

    halts  ⟺  SIR + NG' ⊢ ⊥                          (logic layer: as m254, NG' one more projection)
           ⟺  ZFc + NG' ⊢ ⊥                         (settheory: S_equicons with NG' added, (A) + (B))
           ⟺  ZFC + NG' ⊢ ⊥                         (zfc ac_relcon with NG' added: needs NG' → NG'^L)
           ⟺  ZFC ⊢ ¬NG'  ⟺  ZFC ⊢ GC              (adequacy (i): ZFc ⊢ NG' ↔ ¬GC_std)

Three transfer obligations, plus adequacy:
* (A) soundness `SIR + NG' ⊢ ⊥ → ZFR + NG' ⊢ ⊥`: S_sound relativizes to L inside ZFR, so it needs
  `ZFR + NG' ⊢ NG'^L`. Then regularity_relcon (WF part) needs `ZFc + NG' ⊢ NG'^WF`.
* (B) completeness `ZFc + NG' ⊢ ⊥ → S0 + IR + NG' ⊢ ⊥`: the quotient interpretation qt, so it needs
  `S0 + IR + NG' ⊢ qt(NG')`.
* (C) `ZFc + NG' ⊢ NG'^L` for the ZFC step.
* (i) adequacy, only for the final reading "ZFC ⊢ GC".

### 5.1 Adequacy (i): ZFc ⊢ NG' ↔ ∃ even m ≥ 4 that is not a sum of two primes

(→) Let n be a witness.
1. *n is a finite ordinal.* For A ⊆ n, F = {A, n∖A} is a 2-partition (separation and pairing), so
   LM(A) holds for every A ⊆ n. LM(A) says: for z∈A, z ⊆ n, and A has a least m (m∈k ∨ m=k for all
   k∈A) and a strict-max M (¬M∈k for all k∈A). Applying it to the subsets {x}, {x,y} and {x,y,z}
   gives: ¬x∈x, comparability, asymmetry and transitivity of ∈ on n. So ∈ strictly well-orders n;
   n is transitive (z ⊆ n for every z∈n, from A = n); and n is finite (if ω ⊆ n, ω has no max).
   [Textbook variant: Tr(n) ∧ Trich(n) ∧ strict min and strict max of every nonempty subset gives the
   same, by the definition of a finite ordinal.]
2. *Grid lemma.* If Grid(X;R,C) and X ≠ ∅, then x ↦ (row(x), col(x)) is a bijection X → R×C.
   Part gives unique rows and columns. G (∃!x∈r x∈c) gives surjectivity and injectivity. NT gives
   |R|, |C| ≥ 2. So |X| is composite. Conversely, a composite |X| = k·m gives rows and columns of
   a k×m labelling. Grid(∅;∅,∅) holds.
3. *Ev.* Two(R) gives 1 ≤ |R| ≤ 2, so R ≠ ∅, hence n ≠ ∅ (by NT) and the grid lemma applies.
   NT gives |R| ≥ 2, so |R| = 2 and n = 2·|C| with |C| ≥ 2: n is even and ≥ 4. Bounded Two matters
   here: with an unbounded Two, Ev(∅) would hold via the 0×0 grid.
4. *GF.* Suppose |n| = p + q with p, q prime. Choose A ⊆ n with |A| = p, and let F = {A, n∖A}. GF gives
   a block X ∈ F with |X| ≤ 1 (Small) or Grid(X) (|X| composite, by 2). Both are impossible.
(←) Take n = m (an ordinal) together with the obvious grids. For every 2-partition {A,B} with
|A| + |B| = m, one block is ≤ 1 or composite. Its grid is built by a bijection with k×m.
Also, every block satisfies LM because n is a finite ordinal.

Coq cost: finite cardinal arithmetic in library ZF (|A ⊔ B| = |A|+|B|, |R×C| = |R|·|C|, bijections
with ordinals). This is the largest piece *if* it is done syntactically. Alternative:
model-level adequacy (in HF sets in Coq) plus an informal argument. Lead's call.

### 5.2 (A)/(C): absoluteness for L (and WF)

Let n witness NG' in V (ZFc suffices). n ∈ ω ⊆ L by 5.1.1. Let us check NG'^L.
* The existential witnesses (R, C, the grid of each block, the y of Small, the F bindings) are
  hereditarily finite sets over n. Lemma HF⊆L: every finite subset of L is in L (induction on the size:
  L is closed under pairing and binary union). Iterated twice, P(n) ⊆ L and P(P(n)) ⊆ L.
* The universal quantifier ∀F of GF, relativized to L, only gets weaker. Part^L(n,F) and Two^L(F) are equivalent to
  Part and Two for F ∈ L (bounded formulas over a transitive class). So the conclusion of GF holds in V and
  its witnesses lie in L.
* All remaining quantifiers are bounded (∈ n, ∈ F, ∈ r), or are the equality-guarded ∀F((F=R ∨ F=C) → …)
  and ∃F(F=R ∧ …), which are absolute.
The same argument works for WF in place of L (finite sets of WF sets are WF). It needs no adequacy and
no arithmetic: the HF⊆L lemma plus Δ0-absoluteness for transitive classes.

### 5.3 (B): the quotient transfer  S0 + IR + NG' ⊢ qt(NG')

qt maps ∈ ↦ Mem (= E*: x E* y iff ∃u∈y. x ≈ u) and = ↦ Eqv (≈). It keeps all quantifiers
unrelativized. Work inside S0 + IR + NG' and fix a raw witness n.
1. *Raw finite well-order.* Raw GF applies to every raw subset A of n: the raw complement exists by
   raw separation (S_gic.sepS_use), and the raw pair {A, n∖A} exists. So raw LM(A) holds for all raw A ⊆ n.
   This gives raw transitivity of n, raw comparability, raw strictness, and the raw least element of every
   raw subset.
2. *Rigidity.* x ≈ u with x, u ∈ n implies x = u (raw identity). Proof: let
   D = {v∈n | ∃w∈v. w ≈ v} (raw separation, the formula uses Eqv). If x ≠ u, then by comparability u ∈ x
   (say), so x ∈ D. Let m be the raw least element of D, and w ∈ m with w ≈ m. Then w ∈ n
   (transitivity). The bisimulation relating w and m, applied to the element w of m, gives
   w' ∈ w with w' ≈ w, so w ∈ D. Since w ∈ m and m is least, m ∈ w or m = w, which contradicts raw strictness.
3. *Consequences.* For raw sets s ⊆ n and x ∈ n: Mem x s ⟺ x ∈ s, and Eqv x y ⟺ x = y. For raw
   s, t ⊆ n: Eqv s t ⟺ s and t have the same raw members. Part forces every block, row and column
   to be ⊆ n, so each atom of NG' that is evaluated under its guards means the same raw and in qt.
4. *Clause by clause.*
   * Ev: the raw grid (R, C) is the qt-grid. Its qt-members are the classes of raw rows. Uniqueness
     transfers by 3.
   * GF: given a qt-2-partition F of [n], let c, d be its qt-blocks (from Two^q). Take the raw traces
     t_c = {u∈n | Mem u c} and t_d, and the raw pair f' = {t_c, t_d}. Then f' is a raw 2-partition.
     Raw GF gives raw LM(t_c), raw LM(t_d) and an NP certificate on t_c or t_d. Transfer these to c, d,
     using Eqv c t_c (quotient extensionality, eqv_ext) and qt_inv.
   * The rebinding ∃n∈F and the equality-guarded ∀F / ∃F are handled by qt_inv (invariance under ≈).
   * Small: ∃y ∀x∈X x=y transfers directly (Eq ↦ Eqv, positive).
5. IR is not needed for the transfer itself: strictness comes from the LM strict max. IR is used only
   for the F-normalisation (F = v0∈v0 under binders of label 0), done first, as in m254-logic.

## 6. Effort assessment (honest; calibrated ≈ naive / 3 per past experience)

| piece | content | naive lines | calibrated | risk |
|---|---|---:|---:|---|
| logic layer (m254 Codes/Bundle/Sound/Comp + EnumGB) | bundle' = bundle ∧ NG'; `D (NG code) = NG'_wff` symbolically (Opaque P); SIR+NG' ⊢ closure of the decoded bundle (NG' is an axiom, after F-normalisation); NG' recovered by ∧-elim | 300 | 120 | low |
| L2 / TM layer | regenerate from the new DAG as tg296 did | (generated) | – | low |
| (A)/(C) L- and WF-absoluteness | HF⊆L lemma (finite subsets of L are in L) plus Δ0 absoluteness, applied to this one formula | 500 | 200 | low–medium |
| (B) quotient transfer S0+IR+NG' ⊢ qt(NG') | raw finite well-order from raw GF; rigidity via the D argument; trace lemmas; clause-by-clause transfer with eqv_ext/qt_inv | 1200 | 400–500 | **medium–high: the crux** (new, not in the paper) |
| (i) adequacy ZFc ⊢ NG' ↔ ¬GC_std | finite cardinal arithmetic in library ZF: |A ⊔ B|, |R×C| via bijections with ordinals; finite ordinals; parity | 2500 | 800–1000 | medium (large but routine), or replaced by model-level adequacy |

Summary. The machine side is cheap. On the set-theory side, L/WF absoluteness is easy because every
quantifier after ∃n is bounded by n, by a family of subsets of n, or is equality-guarded. The quotient
transfer is the new and delicate lemma. Its key fact is rigidity: no two raw elements of n are
bisimilar. It holds because LM (least element, strict max, transitivity) is forced on every raw
subset of n, through raw 2-partitions. Part forces every block, row and column to be ⊆ n. Without
that, junk elements bisimilar to points of n would break the transfer. This is why the rows-⊆-n
clause is in Part, and why the formula has no unrelativised ∃ that reaches outside n except
`∃y` in Small, which is harmless. Full syntactic adequacy (i) is the largest single item. It is
standard finite combinatorics in ZF, and it is only needed for the reading "ZFC ⊢ GC" with a
library-standard GC.

## 7. Files

| file | purpose |
|---|---|
| `chosen.json` | the chosen NG' (family module, option switches, role → label map) |
| `ng_final.py` | builds `source_gb.py` / `m254gb_wade.tm`; prints the named and labelled readings; `control` builds the positive control (`source_gbctl.py`, `m254gb_control.tm`) |
| `ngdsl.py` | role-named formula DSL: RPN generation, capture check, conflict graph, greedy labelling, de Bruijn printer, compile with Wade's TMBuilder |
| `cands.py`, `cands2.py`–`cands6.py` | candidate families A–F (section 2); `cands6.py` holds the chosen family |
| `hc.py`, `sa.py` | hill-climbing / simulated-annealing searches over labels and order switches (Idle priority) |
| `modelcheck.py`, `mc_chosen.py`, `mc_grid.py`, `mc_test.py`, `mc_famA.py` | brute-force small-model semantics |
| `spec.py` | `enum_step` with the hand-written `spec.NG` and `bundle = bundle_orig ∧ NG` |
| `validate.py`, `extract_rpn.py`, `rmsim.py`, `bignum.py`, `compiler.py`, `build_dag.py`, `flatten.py` | copied from m254tg/machine and adapted (env `M254GB_SRC` selects another `source_<variant>`) |
| `mutation.py` | atom-level mutation test of `spec.NG` against the compiled RPN |
| `gen.py`, `source_local.py`, `source_orig.py` | the zfc_254 base (`gen.py orig` = 281) |
| `runs/` | search logs, validation logs, snapshots |

