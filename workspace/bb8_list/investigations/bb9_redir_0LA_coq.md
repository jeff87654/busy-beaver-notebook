# 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA: machine-checked halting and score

Opus investigator (inv-bb9-redir-coq), 2026-10-07/08. Scratch and generators: bb9_redir_0LA_coq/ (README.md, NOTES.md).

## Verdict
- **HALTS, machine-checked.** proofs/BB9_redir_0LA.v, `Theorem halt : halts tm c0.`
  check.py output (run from bb8_list/proofs):

      PASS BB9_redir_0LA.v: 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA HALTS (machine-checked, no axioms)

  The file is 204 KB (271 lemmas and theorems). It compiled in 1744 s wall at Idle priority on a heavily loaded PC.
- **Exact score, machine-checked.** proofs/BB9_redir_0LA_bound.v imports the halting file unchanged and compiles in 72 s.
  The halt is in state I reading a 0 (I0 undefined), so the standard score is ones + 1.
- **It beats the BB(9) record, machine-checked against the record's own theorems.** `beats_record` imports
  BB9_record_1RB0RA.v and BB9_record_bound.v unchanged and uses their score_closed and Bx_arrow13 (section 4).

## 1. Theorem statements (printed by Coq; probe bb9_redir_0LA_coq/probe_bound.v, log probe_bound.log)

    halt : halts tm c0
    score_exact : exists c, c0 -->* c /\ halted tm c /\ ones c (6 * b3 + 10 * nn + 6 * (KK / 5) + 23)
    score_closed : exists c, c0 -->* c /\ halted tm c /\ ones c (3 * arrow (KK + 2) 2 5 + 10 * nn + 6 * (KK / 5) + 11)
    b3_closed : 2 * b3 + 4 = arrow (KK + 2) 2 5
    bf_closed : 2 * bf + 4 = arrow 37 2 3
    sigma_lower_bound : exists c N, c0 -->* c /\ halted tm c /\ ones c N /\ arrow (2 * bf) 2 5 < N
    beats_record_formula : forall Bx, 2 * Bx + 4 = arrow 13 2 3 ->
       exists co No, c0 -->* co /\ halted tm co /\ ones co No /\
         3 * arrow (12 * Bx - 9) 2 8 + 108 * (Bx / 5) + 70 + 1 < No
    beats_record : exists cc Nc co No,
       c0 -[ BB9_record_1RB0RA.tm ]->* cc /\ halted BB9_record_1RB0RA.tm cc /\ BB9_record_bound.ones cc Nc /       c0 -->* co /\ halted tm co /\ ones co No /\ Nc + 1 < No
    arrow_agree : forall k a b, BB9_record_1RB0RA.arrow k a b = arrow k a b
    ones_agree : forall c N, BB9_record_bound.ones c N <-> ones c N

Definitions (as printed by Coq):
- nn = (12 * bf + 8) / 5, KK = 2 * nn + 35, b3 = U KK (U KK (U KK 0)).
- bf = proj1_sig bf_sig with bf_sig : {b | b = U 34 (U 34 0)} (sealed).
- U, arrow and ones are exactly as in BB8_champ35_bound.v (arrow 0 a b = a * b, arrow (S k) a b = Nat.iter b (arrow k a) 1).

Print Assumptions gives "Closed under the global context" for halt, score_exact, score_closed, sigma_lower_bound,
beats_record_formula, beats_record, arrow_agree and ones_agree.

In words: let T = 2^^37 3 (37 Knuth arrows). Then bf = (T - 4)/2, n = (12 bf + 8)/5 (about 2.4 bf), K = 2n + 35, and
ones = 3 * (2 ^(K+2 arrows) 5) + 10 n + 6 K/5 + 11. The score is ones + 1. That is about 4.8 bf arrows. The record has
about 12 Bx arrows with 2 Bx + 4 = 2^^13 3.

## 2. What the machine does (literal checks first, then Coq)
Family: Kr ds a r = 0^inf D(d_n)..D(d_1) D(a) D(r+1) D(2) G> 0^inf, with D(m) = (10)^m 1 and ds nearest-first.
The BB(8) record family is Kc ds a b = Kr (map (3d+1) ds) (3a+1) (3b). Kg ds suf a b adds raw suffix tokens.
1. c0 -->* Kg (0^34 2) [] 0 0 in 6397 steps. CDP then gives Kg (0^35) [] 0 bf with bf = U 34 (U 34 0), as for the record.
2. The record's path into its halt (ROUNDS, E3, HOPS, X4, TLPS, FIN; ported verbatim) reaches c_end 34 (12 bf + 9),
   state E reading 0. Here E0 = 0LI.
3. **STAGE0** (generated, explored in 2 s): c_end J (5n+1) -->* Kr (1^(J+2n) 7 6 8 9^n) 1 0 for all J, n.
   - It consists of automatic loops: 5 zero digits are eaten per D9 produced, then the D1 list is rebuilt.
   - It needs 12 bf + 9 = 1 mod 5, i.e. bf = 1 mod 5.
4. Kr (1^(2n+34) 7 6 8 9^n) 1 0 = Kg (0^(2n+34) 2) [6;8;9^n] 0 0. The FINDING's stage-0 target
   [D9^n D8 D6 D4^k D1 | D37 | D18] is a later snapshot of plain champion rules from here (R3 with r = 0 refills D7 each time).
5. CDP clears the digit 2 at depth 2n+34, giving the counter U K 0 with K = 2n+35.
   - Then the suffix token 6 = 3+3 is borrowed (R3 with the borrowed token in the suffix, lemma CLRS): counter U K (U K 0).
   - Again 3 -> 0: b3 = U K (U K (U K 0)).
6. **Stage 2** (generated): Kr (1^(5(w+1)) 0 8 l) 1 r -->* halt in state I reading 0, for every w, r, l.
   - ST2A covers phases 1-2 (zeros given as (D1^5)^u, automatic).
   - S2L_loop15 is a hand-specified transfer loop: one round eats three 5-cell units and grows D(k) and the D1 stack by 3.
     It is proved by mexp.run_round.
   - ST2B and ST2C are automatic; ST2C ends at the halt.
   - Literal check: ones = 2r + 10p + 6m/5 + 23 (m zeros, p D9 tokens), for m = 5..95 step 5 and several p, r.
7. Arithmetic: 2 bf + 4 = arrow 37 2 3 is a power tower 2^2^2^2^y with y >= 1, which is 36 mod 50.
   The proof uses 2^20 = 1 mod 25 and 2^4 = 1 mod 5 and computes no large numbers.
   Hence bf = 25 s + 16, n = 60 s + 40 and K = 5 (24 s + 23).

## 3. Corrections to FINDING_9state_0LA.md
- **The borrow from D3 is an ordinary R3 step.** The 8-state lemma X3 is generic in the borrowed token: D(X+3) -> D(X)
  for all X, including X = 0.
  - The "Stage 1 (literal)" event is a champion-rule snapshot.
  - Jump 1, Stage 1 and Jump 2 together are just CDP plus two suffix borrows (6 -> 3 -> 0).
  - The remark "D0, D2, D3 block a borrow" is wrong for D3.
- **Stage 2 needs only m' = 0 mod 5, i.e. B = 16 mod 25.** On that residue every m' >= 5 halts the same way (the
  symbolic proof covers all w). The mod-7 / mod-35 dependence and the exceptions m' in {0, 7} belong to other residues,
  which take different (also halting) paths in the literal grid. B = 6 mod 7 is not needed.
- The stage-0 target, both jumps and the ones formula 2 R2 + (744 B + 2121)/25 are confirmed, with R2 = 3 b3.

## 4. The comparison with the record, and the open gap
- beats_record_formula is fully machine-checked. For every Bx with 2 Bx + 4 = 2^^13 3, our halting tape has more than
  3 * arrow (12 Bx - 9) 2 8 + 108 (Bx/5) + 71 ones. That expression is the record count documented for
  BB9_record_bound.score_closed (bb9_record_1RB0RA_1LI0LC_coq.md, section 3), with 2 Bx + 4 = arrow 13 2 3 (Bx_arrow13).
- Paper argument, as in Coq (lemmas bf_vs_Bx, Bx_ge6, compare_arith):
  1. bf >= 6 Bx + 10, because 2^^37 3 >= 2^(2^^13 3).
  2. KK + 2 >= 4 bf > 12 Bx - 8.
  3. With K' = 12 Bx - 9: arrow (KK+2) 2 5 >= arrow (K'+1) 2 5 >= arrow K' 2 9 >= 2 arrow K' 2 8, and arrow K' 2 8 >= K' + 3.
- beats_record instantiates this with the record's own constants: BB9_record_bound.score_closed gives the record's
  halting configuration with 3 * arrow (12 * Bx - 9) 2 8 + 108 * (Bx / 5) + 70 ones, where arrow and Bx are
  BB9_record_1RB0RA.arrow and BB9_record_1RB0RA.Bx; arrow_agree converts that arrow to ours. The record halts on I1,
  so its score is Nc; ours is No + 1, and Nc + 1 < No.
- Independent link by the lead: proofs/BB9_redir_0LA_vs_record.v (52 s, both theorems closed) proves
  arrow_agree9 : forall k a b, BB9_record_1RB0RA.arrow k a b = arrow k a b and redir_0LA_beats_record (same shape as
  beats_record: Nr + 1 < No against BB9_record_bound.score_closed). The link is therefore closed twice.
- History: my first read of BB9_record_bound.v was blocked by the permission classifier; the user then approved it.
  Before that I had guessed BB8_champ35_bound.arrow for the record's arrow (wrong module), which is why the first
  attempt to use Bx_arrow13 started evaluating.

## 5. Structure and tooling (bb9_redir_0LA_coq/)
- gen_final.py OUT.v assembles:
  - the autoproof header;
  - the ported 8-state lemmas (h8_*, from BB8_champ35_1RB0RA.v, plus FINx and c_end from BB8_champ35_bound.v);
  - the generated crossing and stage lemmas (gen_machine.py, with a copy of mexp.py);
  - abstract.v.in (Kr/Kg, raw-token rules Kr_R1..R3, Kg rules, CDP, CLRS, init_reach, R4P, STAGE0_Kr, STAGE2_Kr);
  - arith.v.in (arrow, U_closed, sealed bf, tower mod 50) and main.v.in (reach_stage2, halt).
- gen_bound.py OUT.v fills bound.v.in.
- New tool handloop.make_loop(X, v, stacks, use): a transfer loop given by its round-boundary configuration, proved by
  mexp.run_round and emitted by mexp.Gen.loop. It is needed when the explorer never stops at a round boundary.
- phases.py (drive, regroup), inst.py and litcheck.py (instantiate symbolic configurations; exact literal pass-through
  checks), st0.py and p3loop3.py (the machine-specific shapes).
- For the three-cycle sibling ..._1LC1RH_0LH0RF_---0LA, copy st0.py, p3loop3.py and the KR shape in common.py with its
  tail (10)^4 and canonical state F. gen_machine.py and the templates are otherwise generic.
- Compile cost: everything ran at Idle on a saturated PC, where my jobs got a few CPU-seconds per minute.

| part | wall time |
|---|---|
| machine part (dev) | 3625 s |
| abstract part (dev) | 2033 s |
| final halting file | 1744 s |
| bound file | 72 s |

## 6. Lessons
- Coq 8.20 has no Nat.pow_mod. A 6-line pow_mod_nat suffices.
- Nat.div_unique concludes q = a / b, so it needs symmetry.
- `Opaque` inside a Section does not survive the section. Use change instead of simpl near arrow terms in later files.
- A Qed can hang in the kernel even when all tactics finish: a lia whose context holds closed arrow terms may pass in the
  tactic phase, and then the kernel evaluates. Keep every lia over variables (generalize, or set + clearbody first).
  Stating the final comparison as a lemma over plain variables (compare_arith) fixed it.
- An explorer target must use the machine's natural block ((D1 D1)^n, not D1^(2n)), or the final finish_norm fails.
- Before trusting a FINDING "event", check whether the 8-state rule lemmas are generic in that token.

## 7. Reproduce
    cd bb8_list/investigations/bb9_redir_0LA_coq
    python gen_final.py ../../proofs/BB9_redir_0LA.v       # 2 s
    python coqc_idle.py ../../proofs/BB9_redir_0LA.v 14000  # Idle compile
    python gen_bound.py ../../proofs/BB9_redir_0LA_bound.v && python coqc_idle.py ../../proofs/BB9_redir_0LA_bound.v
    cd ../../proofs && python check.py BB9_redir_0LA.v
