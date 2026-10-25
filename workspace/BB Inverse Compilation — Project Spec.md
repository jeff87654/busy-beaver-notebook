# BB Inverse Compilation — Project Spec

Oct 12, 2026 · @Jeffrey Ketchersid

## Goal and hypothesis

Build a pipeline that takes an abstract ordinal-counter program of known growth rate and finds the smallest 2-symbol Turing machine that implements it, with a machine-checked proof. The aim is BB(8)–BB(10) champions that do not descend from the BB(7) champion.

**Hypothesis.** The current BB(8), BB(9) and BB(10) champions all extend the BB(7) champion one state at a time. Each added state buys roughly one more layer of iteration. Wherever the space has been searched well (BB(2)–BB(7)), consecutive champions are unrelated architectures, so the true 8–10 state champions probably look different too.

**Success criteria**

- **Calibration:** the pipeline finds and verifies an f\_ω-class machine at ≤ 7 states. This matches the known BB(7) champion's class, so the pipeline can at least see what is known to exist.
- **Primary:** a verified f\_{ω+1}-class machine at ≤ 9 states with an argument large enough to beat the BB(9) champion, f\_ω(2↑¹³3). Under the textbook rules, f\_{ω+1}(3) = f\_ω(f\_ω(f\_ω(3))) already does, since f\_ω(f\_ω(3)) ≫ 2↑¹³3.
- **Stretch:** f\_{ω·2} or f\_{ω²} at ≤ 10 states.

**Non-goals.** Upper bounds or true BB values; chaotic or Collatz-like champions, which this method cannot see; 3+ symbol domains, except as a cheaper testbed.

## Background: Hardy counters

The target programs are Hardy-hierarchy counters, because they map naturally onto tape blocks: hold an ordinal α and a number n, and step until α = 0.

```latex
H_0(n) = n \qquad H_{\alpha+1}(n) = H_\alpha(n+1) \qquad H_\lambda(n) = H_{\lambda[n]}(n)
```

The key identity is H\_{ω^α} ≈ f\_α, so each target growth class becomes a counter of a particular shape. The runtime of the abstract program is at least H\_α(n₀), and the TM's step count is at least that.

| Target class | Hardy ordinal | Tape structure | Current 2-symbol record at this class |
| --- | --- | --- | --- |
| f\_k (k-fold arrows) | ω^k | k fixed counters | BB(6) is about f₄ |
| f\_ω (Ackermann) | ω^ω | a list of counters that can grow | BB(7), BB(8) |
| f\_ω ∘ f\_ω (iterated Ackermann) | ω^ω · 2 | list + one repeat counter | BB(9) |
| f\_{ω+1} | ω^(ω+1) | list + one top counter | BB(10) |
| f\_{ω·2} | ω^(ω·2) | two lists | none below 14 states |
| f\_{ω²} | ω^(ω²) | list of lists (2D array) | 21 states (constructed) |
| f\_{ω^ω} | ω^(ω^ω) | arrays of growing dimension | 40 states (constructed) |

**Worked example (f\_ω).** Tape layout `1^n 0 1^d₀ 0 1^d₁ 0 … 1^d_k`, representing α = ω^k·d\_k + … + ω·d₁ + d₀. The rules:

1. If d₀ > 0: d₀ −1, n +1.
2. Otherwise, find the lowest nonzero d\_j: d\_j −1, then set d\_{j−1} := n.
3. If every digit is 0: halt.

Starting from a list of length about n₀ with a 1 at the top gives roughly H\_{ω^ω}(n₀) ≈ f\_ω(n₀) steps.

## Architecture

Four components run in a loop: templates become specs, the engine proposes machines, and the verifier either accepts a machine or returns a counterexample. Accepted machines get a growth certificate and a Rocq proof.

&#91;embedded content: pipeline · 6 stages, 1 counterexample loop\]

The only exit from the loop is a full symbolic proof; every failure becomes a new test instance.

**Suggested stack**

- Python for the DSL, orchestration and proof generation.
- Rust or C++ for the enumerator and concrete simulator, the hot loop.
- PySAT with CaDiCaL or Kissat for Engine B.
- Rocq + busycoq for proofs; Claude Code to build and iterate.

## Component 1: rule-template language

The search target is a family of rule systems in one growth class, not one textbook program. Real champions implement sloppy variants, and exact copying is expensive in states.

**Template parameters** (each instantiation is one spec):

| Parameter | Options to start with | Why it matters |
| --- | --- | --- |
| Refill R(n) on a limit step | n, n+1, n+c, 2n+c, "move the block, leave a bigger one" | Exact copy is the costliest subroutine |
| Successor increment | n → n + k, k ≥ 1 | Lets the counter grow as a side effect of a sweep |
| Digit order | counter left/right of digits; digits ascending/descending from the head | Decides how far each sweep travels |
| List growth (ω-level lists) | new digit created at the end, or at the top when exhausted | Needed for anything ≥ f\_ω |
| Block encoding | value v ↔ 1^(v+c); separator 0 or 00; unit `1` or `10` | Zero digits must stay distinguishable from blank tape |
| Initialization | blank tape → any config with α ≥ α\_target, n ≥ n₀ | Startup is usually sloppy in real champions |

**Admissibility rule.** A variant counts if it provably dominates the textbook Hardy counter for the target ordinal. The standing lemma: R(n) ≥ n and k ≥ 1 imply step count ≥ H\_α(n₀), using monotonicity of H\_α in n. Variants that need a weaker comparison are allowed only with their own lemma.

**Partial specification.** The machine only has to be correct on configurations reachable from the blank tape, not on every encoded configuration. This is a large relaxation and should be the default.

**Expressivity check.** Write the BB(6) and BB(7) champions' known rule systems in the DSL (from the wiki analyses). If either cannot be expressed, the template language is too narrow.

## Component 2: synthesis engine

Given a spec and a state budget N, find transition tables whose behavior on concrete test instances matches the spec. Two engines share one interface; start with the first.

**Engine A: spec-pruned TNF enumeration (start here).** Reuse a standard Tree Normal Form enumerator. Run every test instance on the partial table; when an undefined transition is hit, branch over its options. Prune a branch the moment any instance:

- reaches a checkpoint with the wrong encoded configuration,
- exceeds its step budget before the checkpoint,
- halts before the abstract program does.

This is simple, fast in practice, and reuses audited code. Pruning should cut far deeper than plain halting-based TNF, because a wrong rule fails within a few hundred steps.

**Engine B: SAT / bounded model checking (for N ≥ 9 if A stalls).**

- **Table variables.** Per (state q, symbol s): write bit w, direction bit d, one-hot next state over {1..N, HALT}. Symmetry breaking: A0 = 1RB, states numbered in order of first use.
- **Trace variables.** Per test instance i, step t ≤ T\_i, cell p in a window W\_i: tape bit, one-hot head, one-hot state. Standard transition clauses link step t to t+1 through the table variables.
- **Checkpoint.** Each abstract configuration maps to a TM state and head offset (a "phase"); let the solver choose these too. Require that the first time the trace enters the phase, the tape window equals the encoded successor.
- **Size.** With N = 10, W ≈ 60, T ≈ 300 and block lengths ≤ 3, each instance is about 10⁶ clauses. That is fine for CaDiCaL or Kissat with incremental solving.

**Sketches.** Either engine can take pinned fragments (a known bouncer, block shifter or unary incrementer) and search only the remaining transitions. Use sketches when the free search stalls, and record which idioms the winners use.

## Component 3: verifier and CEGIS loop

A candidate that passes the concrete tests is only a hypothesis; the verifier proves each rule for all block lengths or hands back a counterexample.

**Symbolic verification.** Run the candidate on symbolic configurations with variable block lengths (for example `1^(a+1) 0 1^b …`). Use a macro simulator that proves shift rules and counter rules by induction, as Ligocki-style simulators already do. Case-split small values (0, 1, 2) and prove the general case by induction. Each abstract rule yields either a proof that Enc(c) reaches Enc(step(c)) at the first checkpoint, or concrete lengths where it fails.

**The loop.**

1. Synthesize a candidate on the current test set (Component 2).
2. Verify every rule symbolically, plus initialization from blank tape and the halting rule.
3. On failure, add the failing lengths as a new test instance and go to 1.
4. On success, certify growth and export the proof.

**Growth certification.** From the verified simulation: TM steps ≥ abstract steps ≥ H\_α(n₀) by the admissibility lemma. Then compare against the current champion's bound for that N, and record the comparison as its own lemma.

**Cross-check.** Run each verified machine in an independent accelerated simulator on small starting configurations. Agreement here is a cheap guard against a bug in the symbolic prover.

## Component 4: proof export to Rocq

Every verified machine ships with a busycoq proof. No result is announced without one.

- **Semantics.** Use busycoq's TM definitions unchanged; no custom semantics, to keep the trusted surface small.
- **Rule lemmas.** Each symbolically verified rule becomes one lemma over configurations with symbolic exponents, in the style of the existing busycoq champion proofs.
- **Termination and bound.** Ordinal descent of the abstract counter gives halting; the step bound follows from the admissibility lemma. For ordinals below ε₀, check whether Castéran's hydra-battles library supplies Cantor normal form ordinals and Hardy functions; for ω^ω-level counters, a lexicographic order on lists may suffice.
- **Headline theorem.** Keep it short enough to audit by eye: "M halts from the blank tape after at least X steps", with X built from a standard, small definition. The generator should emit this statement from a fixed template, so a human reviews one template rather than every proof.
- **Generation.** The verifier's proof trace should be emitted as Rocq tactics directly, not reconstructed afterwards.

## Milestones

Calibration comes before any claim about 8–10 states: if the pipeline cannot rediscover what is known at ≤ 7 states, its negative results mean nothing.

| # | Milestone | Exit criterion |
| --- | --- | --- |
| M0 | DSL, encodings, concrete simulator, spec checker | Textbook f₂, f₃ and f\_ω programs run correctly at the abstract level |
| M1 | Low calibration | Finds f₂ and f₃-class machines; reports the smallest N for each and compares with BB(4)–BB(6) |
| M2 | Expressivity check | BB(6) and BB(7) champion rule systems are expressible in the DSL |
| M3 | f\_ω calibration | Verified f\_ω-class machine at ≤ 7 states. If it needs ≥ 8, widen templates and repeat M2–M3 |
| M4 | Primary target | Verified f\_{ω+1}-class machine at ≤ 9 states beating the BB(9) bound, with a Rocq proof; also try 8 states against BB(8) |
| M5 | Stretch | f\_{ω·2} or f\_{ω²} at ≤ 10 states |
| M6 | Write-up | bbchallenge wiki entry and Discord post per machine, plus a table of the smallest N found for each template |

The M6 table is useful even with no new champions: the minimum state count per template and growth class is new data about how states buy growth.

## Risks and open questions

The main risk is that the templates encode only what we already imagined, so the pipeline rediscovers our own ideas.

| Risk | Mitigation |
| --- | --- |
| Templates too narrow | Expressivity check against known champions (M2); wide parameterization; allow free "glue" states between pinned rules |
| Search blowup at N = 10 | Spec pruning first; sketches; Engine B; a 3-symbol testbed with fewer states |
| Wrong checkpoint mapping (phase state, head offset) | Let the engine choose it; try several mappings per spec |
| Symbolic proofs for nested counters too hard to automate | Hand-guided induction templates per rule shape; reuse existing simulator provers |
| Errors in the growth comparison for sloppy variants | Every comparison becomes a Rocq lemma, never a hand argument |
| Blind to chaotic or Collatz-like champions | Accepted: this method only produces lower bounds |

**Open questions**

- Which encoding is cheapest for 2-symbol counters: unary with 0 separators, `10` units, or offset blocks?
- Is a 3-symbol pipeline a better first testbed? The BB(8,3) record is f\_{ω+1}-class at 24 transitions, a comparable target.
- What is the compute budget for M4 and M5, and does Engine A finish at N = 9 without sketches?
- Do the BB(7)-lineage champions fall inside the template family? If they do, the search should rediscover them at 8 states, which is a useful check.
