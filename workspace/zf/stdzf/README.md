# stdzf: O'Rear's `prov` vs. the Coq Library of Undecidability's ZF

Goal: replace the paper argument "O'Rear's Hilbert system (zf/coq/Logic.v, `prov`) is equiconsistent
with ZF" with a Coq theorem against a standard, peer-reviewed formalization of ZF: the Coq Library of
Undecidability Proofs (Kirst & Hermes, ITP 2021 / JAR 2023), files `FOL/Sets/minZF.v`, `FOL/Sets/ZF.v`.

## Statements (coq/Std_Main.v, restated in coq/Check.v)

* `prov_iff_ZFc`        : `prov (Wel v0 v0) <-> ZFc ⊢TC ⊥`
* `prov_iff_ZFc_reg`    : `prov (Wel v0 v0) <-> (ZFc + ax_reg') ⊢TC ⊥`   (regularity: zf/regcon)
* `prov_iff_ZFc_fun`    : `prov (Wel v0 v0) <-> RegCon.Main.ZFc ⊢TC ⊥`   (function-symbol signature)
* `prov_iff_ZFcReg_fun` : `prov (Wel v0 v0) <-> RegCon.Main.ZFcReg ⊢TC ⊥`
* `minZFeq_to_prov`     : `minZFeq ⊢TC ⊥ -> prov (Wel v0 v0)` (library theory verbatim)
* `ZFeq_to_prov`        : `ZFeq ⊢TC ⊥ -> prov (Wel v0 v0)`   (library theory verbatim)

`⊢TC` is the library's classical theory derivability (`tprv`, natural deduction `FullND.prv` with
Peirce's law).  `minZFeq`/`ZFeq` are the library's theories verbatim.  `ZFc` (coq/Std_iface.v) is
`minZFeq` with every separation/replacement instance universally closed; this is the axiom set the
library's own semantic entailment uses (axioms must hold under every assignment).  The library's ZF
contains neither regularity nor choice; O'Rear's system has neither either.

Why `ZFc` and not `minZFeq` for the converse direction: in the library's `tprv`, scheme instances keep
their free variables as fixed parameters, and ∀-introduction requires a shifted context, so a
derivation can never use a separation/replacement instance whose parameter is a locally generalized
variable.  Ordinary ZF reasoning (e.g. proving functionality for a replacement) needs exactly that.
Whether `minZFeq ⊢TC ⊥` follows from standard-ZF inconsistency is a parameter-elimination question
not addressed here; `minZFeq_to_prov` gives the direction that holds trivially.

## Layout (coq/)

| file | content |
|---|---|
| Logic.v, L1_L*.v | copies of the verified 393/361/354 developments' logic files (O'Rear's `prov`, pure logic `lprov`, deduction theorem, alpha/specialization lemmas) |
| Std_dB.v | named wff -> library de Bruijn formula `dB` |
| Std_F.v | every `prov` rule/logical axiom is valid in library ND (`prov_Fvalid`) |
| Std_tr.v | library formula -> named wff `tr` (exact under renaming substitutions) |
| Std_H.v | library classical ND is sound for `prov` (`nd_sound`) |
| Std_alpha.v | alpha-equivalent wffs (equal de Bruijn image) are `lprov`-equivalent (`alpha_dB`) |
| Std_gen.v | closures, ND instantiation, round trip `dB` ∘ `tr` (`tr_cl_prov`) |
| Std_iface.v, Std_iface2.v | target theories and the set-theoretic obligations |
| Std_set*.v | ND toolkit, generic closure (recursion) theorem, Zermelo <-> von Neumann infinity |
| Std_br*.v, Haiku_pow.v | bridges: O'Rear's axioms <-> library axioms (Haiku_pow.v: written by a Haiku 5.5 subagent) |
| Std_glue.v, Std_ZFeq.v, Std_Main.v, Check.v | assembly; final statements |

Check: `python check.py` (clean rebuild of coq/ and of zf/regcon/Link.v's chain, then Check.v; prints CHECK PASS).
Incremental build: `python idlebuild.py Std_Main.v`.  The library subset is
vendored in `vendor/` (unmodified, MPL-2.0, see vendor/README.md); `tools/vendor.py` regenerates it
from the clone `ext/undec-8.20` (branch coq-8.20, commit 70dfc56).
