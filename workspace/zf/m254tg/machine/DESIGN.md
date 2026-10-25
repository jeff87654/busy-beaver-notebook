# m254tg machine: zfc_254 with a universe-collection bundle (ZF + GU)

Goal: a TM that halts iff ZF + "every set lies in a Grothendieck universe" is inconsistent. It is the
verified 254 program (`../../m254`, frozen) with one change: in the AX bundle, `C ∧ G'` is replaced by the
merged schema **UG'_φ** (the interface with m254tg-settheory, revised 2026-10-14). The rows ρ1..ρ8, GEN,
the gate `c≠a ∧ c≠b`, MP, DROP, NIP and the coding are unchanged. Compiled with Wade's TMBuilder (the
281-state route).

**Result: 296 states** (`m254tg_wade.tm`, source `source_tg.py`), against the 281 baseline.
**FROZEN 2026-10-14** (accepted by the lead):
`sha256(m254tg_wade.tm) = 1b89758c51ed6eaec9c4581e447c5d74fe2b077270d8c555a1b2d94422c1e520`,
`sha256(source_tg.py) = 25437f9f835e13866cd424d40e2dbf5a223a1ecbe1a3d13f20c9ecdb8139969c`.
Coq interface: `zf/m254tg/logic/coq/EnumTG.v` (frozen; bundle = `CodesTG.bundle_tg`).
Validation ALL OK (section 4).

The interface:
```
UG'_φ := ∀p ∃w [ p∈w ∧ ∀x∈w ( x⊆w ∧ ∃W∈w ∀z (z⊆x → z∈W) )
           ∧ ∀f ∀B∈w ∃C ( ∀a∈B ∀y (φ(a,y,f) → ∃y' (φ(a,y',f) ∧ y'∈C))
                        ∧ ∀y∈C ∃x φ(x,y,f)
                        ∧ ( ∀a∈B ∃y (y∈w ∧ φ(a,y,f)) → ∃U∈w ∀y∈C ∀z∈y z∈U ) ) ]
```
History: the first interface UG_φ (no ∀f; clause 3 concluded `C∈w`) compiled to 288. It was dropped
because it is ZF-provable (see section 7).

## 1. The chosen bundle (decoded formula)

Labels:
* a = param1, b = param2 (after the read), c = param3 = the code of φ;
* **d = c+1** (`par3` followed by an inline `topwff.inc`);
* **f = label 0** (`v_0` = `pushwff`, one token).

φ = decode(c) has input label a, output label b, and its label 0 is f. All other labels of φ are outer
parameters, and they are < c (self-freshness), so c and c+1 never occur in φ.

```
bundle(a,b,c) = UG' ∧ (V= ∧ V∈)                                   [gated: c≠a ∧ c≠b, else 0]

UG' = ∃d [ ∀0 ∀b ( b∈d → ( Y ∧ (T ∧ Q) ) ) ∧ c∈d ]
Y   = ∃c [ ( cl2 ∧ cl3 ) ∧ cl1 ]
cl2 = ∀b ( b∈c → ∃a φ )
cl3 = ∀a ( a∈b → ∃b ( b∈d ∧ φ ) )  →  ∃b [ b∈d ∧ ∀d ( d∈c → ∀c ( c∈d → c∈b ) ) ]
cl1 = ∀a ( a∈b → ∀b ( φ → ∃b ( b∈c ∧ φ ) ) )
T   = ∀c ( c∈b → c∈d )
Q   = ∃c [ ∀d ( ∀c ( c∈d → c∈b ) → d∈c ) ∧ c∈d ]
V=  = a=b → ∀c a=b          V∈ = a∈b → ∀c a∈b
```
Connectives as in zfc_254: `A∧B = ¬(A→¬B)`, `∃x A = ¬∀x¬A`, `¬A = A→F`, F = code 1 = `Rel(0,0)`.
`extract_rpn.py` prints exactly this from the compiled source (`E.d (A.0 A.B (R(B,d) -> ...`).

Roles:
* w = d (the universe);
* f = 0, bound right after w and **outside** the ∀x∈w;
* x = B = b, so one bounded quantifier serves the transitivity/power part and the collection domain;
* C = W = c;
* U = b (x is not used inside the conclusion);
* y∈C uses d, and z∈y uses c;
* z (power) = d, and the ⊆ element variables are c;
* p = c (free).

**The label a occurs only as φ's input.** `∀c(c∈d → c∈b)` occurs twice, once as z⊆x in Q and once as
y⊆U in cl3, so the builder shares it.

### Named reading (roles)
```
UG'_φ(p) = ∃w [ ∀f ∀x ( x∈w → ( Y ∧ (T ∧ Q) ) ) ∧ p∈w ]
  Y = ∃C [ ( ∀y(y∈C → ∃x' φ(x',y,f))
             ∧ ( ∀a(a∈x → ∃y(y∈w ∧ φ(a,y,f))) → ∃U(U∈w ∧ ∀y(y∈C → ∀z(z∈y → z∈U))) ) )
           ∧ ∀a(a∈x → ∀y(φ(a,y,f) → ∃y'(y'∈C ∧ φ(a,y',f)))) ]
  T = ∀u ( u∈x → u∈w )
  Q = ∃W [ ∀z ( ∀u(u∈z → u∈x) → z∈W ) ∧ W∈w ]
```

### Pure-logic steps from the interface UG'_φ ∧ V∈ ∧ V=
1. `∀x∈w X ∧ ∀f ∀B∈w Y` becomes `∀f ∀x(x∈w → (Y ∧ X))`. f is not free in X, so ∀f can be pulled out
   over the conjunction. The two bounded ∀ over w are merged (B renamed x).
2. Conjunct order/association: p∈w last; Y before X; T before Q; `(cl2 ∧ cl3) ∧ cl1`;
   `∃W∈w A` is written `∃W(A ∧ W∈w)` and `∃U∈w A` is written `∃U(U∈w ∧ A)`; `∃y'(y'∈C ∧ φ)`;
   `∃y(y∈w ∧ φ)`.
3. The outer `∀p` is the free label c.
4. `V= ∧ V∈` instead of `V∈ ∧ V=`.

Why ∀f sits outside ∀x and not just before ∃C: with b = 0, a `∀0` inside the ∀x scope would shadow
x = B. Outside, x's binder shadows f instead. That is harmless (collision (5)).

### De Bruijn reading (library order; φ: $0 input, $1 output, $2 = f, params shifted past all binders)
`φ⟨i,j,k⟩` = φ with $0 ↦ $i, $1 ↦ $j, $2 ↦ $k at the point of use.
```
UG' = ∃[ ∀[ ∀[ $0∈$2 → ( Y ∧ (T ∧ Q) ) ] ] ∧ p∈$0 ]          (∃: w=$0; ∀: f=$0; ∀: x=$0, f=$1, w=$2)
Y   = ∃[ ( ∀[ $0∈$1 → ∃[ φ⟨0,1,4⟩ ] ]                                         (C=$0, x=$1, f=$2, w=$3)
         ∧ ( ∀[ $0∈$2 → ∃[ $0∈$5 ∧ φ⟨1,0,4⟩ ] ]
             → ∃[ $0∈$4 ∧ ∀[ $0∈$2 → ∀[ $0∈$1 → $0∈$2 ] ] ] ) )
       ∧ ∀[ $0∈$2 → ∀[ φ⟨1,0,4⟩ → ∃[ $0∈$3 ∧ φ⟨2,0,5⟩ ] ] ] ]
T   = ∀[ $0∈$1 → $0∈$3 ]                                                     (u=$0, x=$1, f=$2, w=$3)
Q   = ∃[ ∀[ ∀[ $0∈$1 → $0∈$3 ] → $0∈$1 ] ∧ $0∈$3 ]                           (W=$0, x=$1, f=$2, w=$3)
```
Index checks, with each binder listed as the variables in scope at that point:
* cl2: ∀y gives y=$0, C=$1. ∃x' gives x'=$0, y=$1, C=$2, x=$3, f=$4.
* H: ∀a gives a=$0, C=$1, x=$2, f=$3, w=$4. ∃y gives y=$0, a=$1, f=$4, w=$5.
* U: ∃U gives U=$0, C=$1, x=$2, f=$3, w=$4. ∀y gives y=$0, U=$1, C=$2. ∀z gives z=$0, y=$1, U=$2.
* cl1: ∀a gives a=$0, C=$1, x=$2, f=$3. ∀y gives y=$0, a=$1, f=$4. ∃y' gives y'=$0, y=$1, a=$2, C=$3, f=$5.
* Q: ∀z gives z=$0, W=$1, x=$2. ∀u gives u=$0, z=$1, W=$2, x=$3.

## 2. Variants measured (Wade TMBuilder, states incl. 62 framework states)

| variant | formula | bundle tokens | states |
|---|---|---:|---:|
| orig | zfc_254 `(C ∧ G') ∧ (V∈ ∧ V=)` (baseline, reproduced) | 93 | **281** |
| **UG' A (chosen)** | interface clause 3 (`→ ∃U∈w ⋃C ⊆ U`), f = 0, section 1 | 144 | **296** (best of 3,072 orders) |
| UG' A, other U labelings (using a) | top 40 orders × 8 labelings | 144 | 296 (no gain; would break a=b) |
| UG' B | `→ C∈w` + per-x `∃U∈w ∀t∈x ∀z∈t z∈U` (U=c, t=d, z=b) | – | 300 (best of 9,216 orders) |
| optional extra: union bound inside Q's W (`→ C∈w`; not interface-equivalent, measured after freeze) | `∃W∈w(∀z(z⊆x→z∈W) ∧ ∀t∈x ∀z∈t z∈W)` | – | 299 (best of 3,072 orders) |
| UG (superseded interface) | section 7 | 121 | 288 |
| UG, other designs | fresh label Rel(Rel(a,b),c): 289; w=c,C=c+1: 294 (unsound at c+1=a); old C∧G' + separate clause: 304; `C⊆w → C∈w`: 285 (too weak) | | |

Notes.
* Wade's builder factors repeated subsequences greedily. Cost is roughly the grammar size, not the
  token count, so the order search matters (288–299 for one UG formula).
  The searches: `search.py` (UG), `search2.py` (UG'). Logs are in `runs/`.
* **Label for f.** Label 0 is the cheapest: one `pushwff`, used once. The u parameter is not kept in any
  register after AX (it is read straight into topwff for ρ8), so using it needs new register code.
  Reusing a or b fails: f = a would be shadowed by the input binder, and f = b inside ∀x would shadow B.
* **Two φ-fresh labels (c, c+1) are needed** because C (cl1) and w (H) are both referenced inside φ
  contexts with a, b bound, and `C∈w`/`U∈w` needs them distinct.
* Not used (not pure-logic equivalent): one container W for both the power and the union bound. It is
  probably smaller, but it is a different axiom.

## 3. Collision analysis (`collide2.py` enumerates every identification mechanically)

The gate closes (current := 0 = truth) iff c = a or c = b. Always c+1 ≠ c and c+1 ≠ 0. With the
gate open, `collide2.py` enumerates every partition of {a, b, c, c+1, 0}, re-resolves every variable
occurrence, and reports vacuous guards, mis-bound atoms and mis-bound φ arguments.
**No atom of T, Q or the U clause is ever mis-bound.** The only effects are below. IR = `∀x ¬x∈x`;
SUIR = equality + UG' schema + IR.

| # | case | effect on the decoded formula | why it is SUIR-provable |
|---|---|---|---|
| 1 | a = b | guards of cl1 and of H become `a∈a`, vacuous by IR (H true, cl1 true). cl2 becomes `∀y∈C ∃x ψ(x)` (ψ: φ with input = output = x). | Use the w of any distinct-name instance at p. For each x∈w take C = ∅: cl2 is vacuous, and the conclusion `∃U∈w ∀y∈∅ …` holds for any U∈w (e.g. p). An empty set exists (cl2 of any instance with φ = F). Uses IR. |
| 2 | c+1 = a | only H changes, to H' = `∀a∈B ∃y(y∈a ∧ φ)` (w captured by the input binder) | H' → H by T: a∈B∈w gives a⊆w (T at B, then T at a), so y∈w. Same w, C, U as the distinct-name instance for the same φ. No IR. |
| 3 | c+1 = b (in any partition, e.g. with a, or with c=0 / a=0) | top guard `∀b(b∈b → …)`, vacuous by IR. Left: `∃w(c∈w)` | p∈w of any instance. Uses IR. |
| 4 | 0 = a | φ's label 0 *is* its input label, so f has no separate occurrence and `∀0` is vacuous | literally the UG' instance for φ'(x,y,f) := φ(x,y) (no $2) |
| 5 | 0 = b | x's binder `∀b` shadows f, and φ's label 0 is its output; `∀0` vacuous | the UG' instance for φ' without $2 |
| 6 | 0 = c | φ = decode(0) = τ has no labels (F read as closed via IR, as before). `∀0` is vacuous; C's binder ∃0 shadows nothing used. p = c = 0 sits outside ∀f. | the UG' instance for φ = τ |
| 7 | combinations (a=b with 0=c; a=b=0; c+1=a with 0=b or 0=c; c+1=a=b; …) | exactly the composites of 1–6 (listed by the tool, no other mismatch) | compose the arguments |

### Collision lemmas the logic layer must prove

Notation. UG'(φ) is the closed schema axiom of SUIR for a de Bruijn φ ($0 input, $1 output, $2 f,
$(k+3) params). `Body_H(φ)` is the UG' matrix of section 1 with hypothesis H. "Decoded" means
`dB(D(bundle a b c))` restricted to its UG' conjunct (the V= ∧ V∈ part is pure logic in every case, since
c ∉ {a,b}). All statements are about the ∀-closure over the free labels (p = c and φ's outer params).

* **COL-ab (a = b).** The decoded formula has the shape
  `∃w [ ∀f ∀x ( x∈w → ( ∃C [ ( ∀y(y∈C → ∃x' χ) ∧ ( ∀i(i∈i → R1) → ∃U(U∈w ∧ ∀y(y∈C → ∀z(z∈y → z∈U))) ) )
                              ∧ ∀i(i∈i → R2) ] ∧ (T ∧ Q) ) ) ∧ p∈w ]`
  for some formulas χ, R1, R2 (χ = φ with input = output; R1, R2 = the old bodies of H and cl1). T and Q
  are exactly as in the distinct case.
  Lemma: `SUIR ⊢ ∀p (that formula)` for all χ, R1, R2.
  Proof:
  1. Take w from UG'(⊥) at p. This gives p∈w, and T and Q for every x∈w and every f.
  2. Take C := e, any empty set. One exists: cl2 of UG'(⊥) at x := p gives a C with `∀y∈C ∃x ⊥`.
  3. Take U := p.
  4. `∀i(i∈i → …)` holds by IR.
  This covers every partition containing a=b, including with 0 or c = 0.
* **COL-da (c+1 = a, a ≠ b).** The decoded formula is `Body_{H'}(φ)`, i.e. the UG' matrix with H replaced
  by `H' = ∀i(i∈x → ∃y(y∈i ∧ φ(i,y,f)))`.
  Lemma: `SUIR ⊢ UG'(φ) → ∀p Body_{H'}(φ)`.
  Proof: same w, C, U. H' → H because i∈x and x∈w give x ⊆ w and then i ⊆ w (T at x, then T at i),
  so y∈i gives y∈w. No IR is used. If also 0 = b or c = 0, apply COL-f to φ first.
* **COL-db (c+1 = b, any partition containing it).** The decoded formula is
  `∃w [ ∀f ∀x ( x∈x → R ) ∧ p∈w ]` for some R.
  Lemma: `SUIR ⊢ ∀p ∃w (∀f ∀x (x∈x → R) ∧ p∈w)`.
  Proof: take w from UG'(⊥) at p; the guard is false by IR.
* **COL-f (0 = a, 0 = b or c = 0; c+1 ≠ a, b; a ≠ b).** No new lemma.
  `dB(decoded) = UG'(φ')` literally, where φ' = dB(φ) has no free $2:
  * 0 = a: label 0 is the input, $0;
  * 0 = b: label 0 is the output, $1, and x's ∀b shadows f;
  * c = 0: φ = τ, which has no labels once F is closed.
  So it is a schema instance. f = p (p = c) and f = c+1 cannot occur: f = 0 < c+1, and c = 0 is the
  case just covered, with p outside ∀f.
* **F literals.** `Rel(0,0)` inside `∀0` (and, for 0 = a/b, inside the input/output binders) refers to the
  bound variable. The existing IR normalization `x∈x ↔ ⊥` (under binders of v0) applies unchanged.

Further remarks:
* **F under ∀0.** Every literal F = `Rel(0,0)` inside the scope of `∀0` now refers to f. IR-normalization
  (`x∈x ↔ ⊥` for any x, under binders of v0) makes this harmless. The logic layer already handles it,
  since a = 0 bound v0 before.
* **Labelings where a plays a role in Q, T or U fail at a = b.** z, W or U captures x, giving
  `∀z z∈W`-type statements refutable with IR. Hence the a-free labeling.
* **No 0/τ collapse.** Every `wim` in the bundle has a nonzero second argument.
* **NIP argument unchanged.** The bundle's top code is `wa(…)`, an Imp code (≡ 0 mod 4), so the
  completeness-macro NIP argument still holds.
* **Completeness (machine side of 7.4).** For a de Bruijn φ ($0 in, $1 out, $2 f, $(k+3) params), choose
  a named version with input a and output b (a, b ≥ 1, distinct), f on label 0, and the params on other
  labels. Pad it so that c exceeds every label. The gate is then open and no collision occurs.

## 4. Validation (all in this directory)

| check | result |
|---|---|
| `gen.py` reproduces the zfc_254 bundle exactly and recompiles to 281; `gen.tgp()` = search2 render of the chosen order | OK |
| `extract_rpn.py` (stubbed `axioms()`, symbolic RPN; `Succ` for c+1, label 0 via `v_0`) | prints the formula of section 1 |
| `validate.py 20000` (`validate.log`): helper closed forms vs brute force | 0 mismatches |
| symbolic RPN vs hand-written `spec.bundle` (200 params; forced c∈{a,b,a−1,b−1}, a=b, and a/b/c = 0) | 0 mismatches (a mutation test is caught 200/200) |
| 5,000 unaccelerated main runs vs `spec.enum_step` | 0 mismatches |
| 20,000 accelerated runs, incl. forced collision AX commands (c+1=a, c+1=b, a=b, a=0, b=0, c=0) | 0 mismatches. About 5,400 gate-open AX samples, of which (overlapping): 0=c 600, c+1=a 490, c+1=b 410, a=b 380, 0=a 140, 0=b 140 |
| `compiler.py` macro contracts, 300 rounds, with extra bundle leaves at a=b, c+1=a, c+1=b, a=0, b=0, c=0 (`runs/compiler_ugp.log`) | 5,700 contracts, 0 failures |
| rebuild determinism (`gen.py tg; build_dag.py`) | identical .tm |

`spec.py`: `bundle_UG(a,b,c)` / `bundle(a,b,c)` are hand-written, independently of gen.py's AST.
`enum_step` is otherwise unchanged.

## 5. Comparison: GU on the 335-state ZF machine (`z335gu/`, measured)

Baseline R3Y1_335 reproduced (335). The R3s fiber-bounded REP (56 tokens) is replaced by UREP (151
tokens, new variable v5): REP's conclusion, plus "the image lies in a transitive w satisfying REP
relativised to w, for every v5":
```
REPhyp -> E. v1 ( IMG(v1) /\ E. v4 ( v1 e. v4 /\ trans(v4) /\
                   A. v5 A. v0 ( v0 e. v4 -> ( REPhyp with E. v1 in v4 -> E. v1 ( v1 e. v4 /\ IMG(v1) ) ) ) ) )
```
Here v5 plays the role of UG''s f: a relation quantified inside, after w.

| variant | plain compile | after ILS |
|---|---:|---:|
| R3Y1_335 | 335 | 335 |
| UREP replacing REP | 379 | 364 |
| UREP, INF dropped (INF plausibly derivable, not proved) | 365 | 351 |

So GU costs about +16 to +29 states on the Wade-style ZF machine, versus +15 here (281 → 296).
Neither text is proved. The 335 caveat: the REP formula may mention v4/v5, which was argued harmless
for V_κ only informally.

## 6. Files

| file | purpose |
|---|---|
| `source_tg.py` | the m254tg source (`gen.py tg`; only the bundle slice of `axioms()` changed) |
| `m254tg_wade.tm` | the compiled 296-state TM (`python build_dag.py`) |
| `gen.py` | formula AST → RPN, variants (`tg` = UG' chosen, `superseded_ug288` = old UG, source `source_superseded_ug288.py`), source generation, compile |
| `search2.py`, `collide2.py` | UG' order/label search; collision enumeration (`python collide2.py A`) |
| `search.py`, `collide.py`, `tryfinal.py` | the same for the superseded UG |
| `spec.py`, `validate.py`, `extract_rpn.py`, `rmsim.py`, `bignum.py`, `compiler.py`, `build_dag.py` | copied from m254/logic and adapted (env `M254TG_SRC` selects another `source_<variant>`) |
| `runs/` | search logs, `m254_wade_baseline281.tm`, `SUPERSEDED_m254tg_UG288.tm`, quick-validation logs |
| `z335gu/` | the 335 comparison |

## 7. History: the first interface UG (288 states, superseded)

UG_φ had no ∀f (all φ parameters were fixed before w), and clause 3 was `H → C∈w`. Its machine version
was the formula above without `∀0` and with `c∈d` as the cl3 conclusion; order-optimised it reached 288.
Settheory/lead found it ZF-provable. Reflection makes `C∈w` free when the parameters are fixed before w.
Even with the relation quantified after w, power containers plus image bounding do not give union
closure (a singular strong-limit counterexample). Hence UG'.
