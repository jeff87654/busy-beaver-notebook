# dl:193804 NOBOUNDARY machine 1RB0RB_1RC0RB_0LD1LF_1RH1LE_0LC0LF_1LG1RE_1LH1LE_0RA---

Investigator: inv-193804 (Opus 5.5, bb8-investigator workflow), 2026-10-08. Scratch scripts are in this folder.

## Verdict

**Never halts. PROVED: `python check.py BB8_193804_1RB0RB.v` PASSes** (machine-checked, no axioms). The proof
compiles in about 35 s. The only halting transition is H1.

- **Not a record.** The machine is a nested base-4 count-down. One cycle takes the configuration from level n
  to level n+1, so the tape grows by 4 cells per cycle. Each cycle costs about (5+sqrt 17)/2 ≈ 4.56 times
  more steps than the one before. Cycles start at steps 256, 1033, 4566, 20670, 94123, 429172 and 1957505.
- **Proof file.** `bb8_list/proofs/BB8_193804_1RB0RB.v` is hand-written; development copies are in `coq/`
  (M1..M5).
- **Why automatic methods failed.** Plain n-gram CPS (up to 20/3, 3/20, 8/8), annotated ngann (6..10, ANN 1/2,
  g on/off), rctl/tctl run-length CTL, and a new window + run-parity CPS (`cps/ngpar.cpp`) all fail fast.
  - Halting is excluded only by the depth of zeros on the left stack below the top run of 1-digits.
  - That depth depends on the count-down state of the right digits, a correlation across unbounded runs.

## 1. H-visit rewriting system (exact, all m, any context)

At every visit of state H the tape is a sequence of digits `0 1^d`, and the head is on the `0` of a digit.
- **Left of the head (L):** digits 0 or 1, written `[0]` / `[1;0]` nearest cell first.
- **Right of the head (R):** digits 0..3.

Between consecutive H visits exactly one rewrite happens. In `L | R`, L has its top last and R has the head
digit first.

| rule | rewrite | steps |
|---|---|---|
| R1 | `L \| 3, b+1, ...  ->  L 0 \| 3, b, ...` | 13 |
| R2 | `L \| 3, 0, ...  ->  L 1 \| 0, 1, ...` | 10 |
| R4 | `L \| 0, 3, b+1, ...  ->  L 1 \| 3, b, ...` | 14 |
| R3(m) | `L 0 0 1^(2m+1) \| 0, 1, u+1, T  ->  L \| 3^(m+2), u, T` | left sweep over (01)^(2m+1) |
| R5(m) | `L e 0 0 1^(2m+1) \| 0, 1, 0, T  ->  L (e+1) \| 0, 3^(m+1), 1, T` | same sweep |

**Stuck (possibly halting) cases.** These never occur:
- a top 1-run of even length;
- fewer than 2 zeros below the top 1-run;
- e = 1 in R5 (this would create a left digit 2);
- right fronts (0,0,..), (0,2,..), (0,3,0,..).

**Checks.**
- `micro.py` collected the H-to-H rewrites.
- `cmpabs.py 3000000 1000`: the string-level abstract system equals the TM on all 218k H visits up to 3M steps.
- `dig.py` / `digrun.py` run the digit-level system (2M abstract steps, no stuck case, no digit > 1 on the left).
- In Coq, R1/R2/R4 and the sweep pieces ST3/EN3/ST5/EN5/LOOP are proved by `start_progress`. LOOPn, R3m and
  R5m are proved for all m.

## 2. Configuration family and rules

The family is `Sc(P, j, T) = (P 1 | 0, 3^j, 1, T)`.

**Main lemma (SA).** For all P, T and j >= 0:
`Sc(P, j+1, T) -->* Sc(P 1 1, j, T)`.
- P and T are never read.
- The number of abstract steps is 2, 10, 46, 210, 958, 4370, ..., with s(j+1) = 5 s(j) - 2 s(j-1).
- Checked numerically in `stest.py` for 9 different P, 5 different T and j <= 6.

**Block lemmas.** These are the base-4 count-down. The right digits after the carrier 3 form a number, and
each unit of it pushes one 0 onto the left stack.

| lemma | statement |
|---|---|
| BL(k) | `(Q 0^z \| 3,3,3^k,u+1,T) -->* (Q 0^(z+1) \| 3,3,3^k,u,T)` for every z >= 0 |
| Z_j(k), j >= 1 | `(Q 0^(z+3j-1) \| 3,3,3^k,0^j,u+1,T) -->* (Q 0^z \| 3,3,3^(k+j),u,T)` |
| W_j(k) | `(Q 0^(z+3j) \| 3,3,3^k,0^j,0,0T') -->* Sc(Q 0^z, k+j+1, T')` |
| Cas(i,j) | `(P 0^(3j) 1^(2i+1) \| 0,1,0^j,0Y) -->* (P 1^(2(i+j)+1) \| 0,1,0Y)` |

Cas is a borrow through j zero digits. It uses R5 followed by SA iterated.

Numerical checks: `ftest.py` (BL), `ztest.py` / `zjtest.py` (Z_j, W_j, random Q) and `wtest.py`.

**How the lemmas compose.**
- BL(k+1) = BL(k)^3 ; Z_1(k).
- Z_j(k+1) = BL(k)^3 ; Z_(j+1)(k).
- Z_j(0) = R1^3 R2 ; Cas(0,j) ; R3(j).
- W_j(k+1) = BL(k)^3 ; W_(j+1)(k).
- W_j(0) = R1^3 R2 ; Cas(0,j) ; R5(j).
- SA(1) uses R4 R1 R1 R2 R3(0) and then W_0(0).
- SA(j+2) uses the same prefix, then the loop G(i,r): `(Q|3,3,3^i,2,3^r,1,T)` takes BL(i)^2, then Z_1(i), and
  repeats. It ends with Z_1 and then W_0(i+1).

**Induction order.** Give SA(j) level j+1, BL(k) level k, Z_j(k) level j+k, and W_j(k) level j+k+1. Every lemma
then uses only lower levels, or lemmas at the same level proved earlier in this order:
1. SA;
2. Z, by induction on k;
3. W, by induction on k;
4. BL.

Coq does this in `Lv_all`, using `strong_induction`.

**Top level.**
- The blank tape reaches `Sc(blank, 3, blank) = 0^inf 1 H> 0 (0111)^3 01 0^inf` at step 256.
- Then `Sc(blank,n,blank) -->* Sc(1^(2n), 0, blank) = (1^(2n+1) | 0,1)`.
- R5(n) then uses the blank zeros as `e 0 0` and gives `Sc(blank, n+1, blank)`.
- `progress_nonhalt_simple` finishes the proof.

## 3. Coq proof

- **File.** `bb8_list/proofs/BB8_193804_1RB0RB.v`, 446 lines, hand-written.
- **Machine-level layer.** R1, R2, R4, LOOP, ST3, EN3, ST5 and EN5 are proved by `start_progress`. LOOPn,
  R3m and R5m are proved by induction or composition.
- **Tape identities.** pow_snoc, zeros_add, zeros_shift, alt0, two_pow and R3_tail.
- **Family layer.**
  - Definitions: `Sc`, `SA_at`, `BL_at`, `Z_at`, `W_at`.
  - Base cases: SA0, BL0, PRE, SAPRE.
  - Lemmas: SAn, Cas, BL3, ZK0, WK0, ZKS, WKS, BLS, SA1, Gloop, SAgen.
  - `Lv_all` (strong induction) and `SA_all`.
- **Top level.** Sc_blank, cycle, init (256 steps by `execute`) and `Theorem nonhalt : ~ halts tm c0`.
- **check.py result:**
  `PASS BB8_193804_1RB0RB.v: 1RB0RB_1RC0RB_0LD1LF_1RH1LE_0LC0LF_1LG1RE_1LH1LE_0RA--- never halts (machine-checked, no axioms)`.
- A row has been added to the Proved table in `proofs/README.md`.

## 4. Score / record comparison

The machine does not halt, so it has no score. Its growth is plain exponential:
- the tape grows by 4 cells per cycle;
- the number of steps per cycle grows by about 4.56 times per cycle.

It is not record-relevant.

## 5. Methods tried that failed (for the toolbox)

| method | settings | result |
|---|---|---|
| ngcps2 | 2/2, 4/4, 8/8, 3/20, 20/3 | H1 fails within seconds |
| ngann | windows 6..10, ANN 1/2, g on/off | fails immediately |
| rctl | several settings, zero-run moduli up to 12 | spurious H1 after a C1 F0 G0 sweep onto `101 00 [C1]` |
| tctl | token runs, counts mod 2 | spurious H1 |
| `cps/ngpar.cpp` (new) | window + run1/run2 lasso counters (alternating-run parity) | fails; spurious right fronts such as (0,2,...) appear after unfolding |

All runs were short and in the foreground.

## Reproduction

    cd bb8_list/investigations/bb8_193804_1RB0RB1RC0RB
    python t1.py 3000000          # cycle times (left/right records)
    python micro.py 100000 1000   # H-to-H rewrites
    python cmpabs.py 3000000 1000 # abstract system == TM on all H visits
    python digrun.py 2000000      # digit-level system, no stuck case
    python stest.py; python ftest.py; python zjtest.py; python wtest.py   # SA, BL, Z_j, W_j
    cd ../../proofs && python check.py BB8_193804_1RB0RB.v

## Open questions

- The sibling `1RB0RB_1RC0RB_0LD1LG_1RH1LE_0LC0LF_1LG---_1LH0RE_0RA1LD` is also OPEN in
  `ngcps_results.tsv`. It may yield to the same H-visit digit analysis. This was not examined.
