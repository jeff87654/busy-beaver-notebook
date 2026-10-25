# C04 / M8: Coq proofs, packaged for outside checking

Two Turing machines, both checked here:

* **M8**: the 8-state machine `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---`;
* **C04**: the 9-state machine `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF`.

For each, `main/Statement.v` claims that the machine, started on the blank tape:

* halts;
* has a well-defined score σ (the number of 1s when it halts);
* has `f_ω(f_ω(12B+26)) < σ < f_ω(f_ω(12B+27))`, where `2B+4 = 2↑^13 3`;
* has `f_(ω+1)(3) < σ < f_(ω+1)(4)`;
* has `σ > 12·(2↑^37 3) + 59`, the score of the current BB(8) entry.

It also claims that the two machines have the same score.

## What you have to trust

You only need to read and trust these files, plus Coq itself:

| file | what it is | size |
|---|---|---|
| `main/Statement.v` | the claims, written from scratch: a small parser for machine strings, the blank start, the ones count, Knuth arrows, the fast-growing hierarchy | 223 lines |
| busycoq `verify/TM.v` (commit `bd2e36f`) | the Turing-machine semantics: `step`, `multistep`, `evstep`, `halted`, `halts` | ~100 lines that matter |
| `lib/BB92.v`, `lib/Individual92.v`, `m8/BB82.v`, `m8/Individual82.v` | busycoq instantiated for 9 and 8 states (they declare the states A.. and the symbols S0, S1) | 35-45 lines each |

You do **not** need to trust the other ~200 files (about 15 MB). Most of them are generated step-by-step machine
lemmas. `main/Check.v` proves `Check.all : Statement.All` from them, and the kernel checks that proof. `verify.sh`
then writes its own audit file, which runs `Check (Check.all : Statement.All)` and `Print Assumptions Check.all`. The
answer must be `Closed under the global context`: no axioms, no admitted lemmas, no parameters.

A 10-minute review of `Statement.v`:

1. Section 1 defines `iter`, `arrow` (with `arrow 1 a b = a^b`), `f`, `f_omega`, `f_omega1` and `BB8_entry_score`.
2. Section 2 defines `cell` / `well_formed`: transition (state i, symbol j) is the 3 characters at position
   `7i + 3j` of the string, and `---` means undefined.
3. Section 3 has the two machine strings. For each machine, `M` is decoded from its string (the tables in the
   comments are for reading only). `start` is the blank tape in state A, and `ones c N` means that the tape of c is
   a finite word padded with blanks holding N ones. `score N` means that M reaches, from `start`, a halted
   configuration holding N ones. `claims` lists the claims above.
4. Section 4: `All` is both `claims` and the equality of the two scores.

Compare `sha256sum main/Statement.v` with the value printed at the end of `verify.sh` and with the one published
next to the proofs.

## Run it

**Linux / macOS** (Coq 8.20.1, git, GNU make):

    ./verify.sh -j 8

**Docker** (nothing to install except Docker):

    docker build -t c04m8-verify .
    docker run --rm -e J=8 c04m8-verify

**Windows** (Coq Platform 8.20~2025.01 and Git for Windows; there is no `make`, so the built-in scheduler is used).
Run this in Git Bash:

    COQBIN=/c/Coq-Platform~8.20~2025.01/bin/ ./verify.sh -j 8
    # to share the machine politely: every coqc at Idle priority, with a 6 GB memory cap
    COQBIN=/c/Coq-Platform~8.20~2025.01/bin/ COQC_WRAPPER="python tools/winidle.py" ./verify.sh -j 4

`verify.sh` does the following:

1. clones busycoq into `_busycoq/` (or uses `BUSYCOQ=...`), checks out `bd2e36f` and checks that it is at that
   commit with clean sources, then compiles the 7 busycoq files it needs;
2. writes `_CoqProject` and builds every file. With `make`, it uses a `coq_makefile` Makefile with `-j N`.
   Otherwise (or with `--no-make`) it uses its own scheduler on `coqdep`'s dependency graph, largest files first;
3. compiles `main/Check.v` and the audit file. `Check.all` must have type `Statement.All` and be closed under the
   global context;
4. runs `coqchk`, the independent kernel checker, on `Main.Check` and, recursively, everything it depends on. It
   must succeed and report no type-in-type, no unsafe fixpoints and no assumed positivity. Its axiom list covers the
   whole loaded environment, not one theorem. It must name only the four axioms that busycoq's `LibTactics.v` and
   the standard-library modules it loads declare: `inj_pair2`, `proof_irrelevance`,
   `functional_extensionality_dep`, `eq_rect_eq`. The audit in step 3 shows that `Check.all` uses none of them;
5. prints `VERIFY: PASS` with the times and the SHA-256 of `Statement.v`. The exit status is 0 only on PASS.

`--no-coqchk` skips step 4. Logs go to `_verify/`.

## Time and memory

| machine | J | build | Check.v + audit | coqchk |
|---|---|---|---|---|
| shared 16-core laptop, Idle priority (measured, see below) | 4 | TBD | TBD | TBD |
| GitHub runner, 4 vCPU (previous unsplit runs) | 4 | ~1 h 32 min | ~6 min | |

Memory: under 1.5 GB per coqc; coqchk TBD.

The time is almost all in the generated machine lemmas. About 80% of it is busycoq's `step` tactic (one
`simpl` over the whole tape per machine step), about 12% is the kernel checking the proofs at `Qed`.

## Layout

| dir | logical path | content |
|---|---|---|
| `main/` | `Main` | `Statement.v` (trusted), `Check.v` (the bridge) |
| `lib/` | `BB8` | busycoq for 9 states; fw2's files (the comparison machine of the BB(9) proof) |
| `dev/`, `k31/` | `Dev`, `K31` | the C04 halting proof (generated machine lemmas `G_*`, `K_*`, and the abstract layer) |
| `score/`, `fgh/` | `Score`, `Fgh` | the score: lower bound, upper bound, exact value, FGH bracket |
| `m8/` | `M8` | busycoq for 8 states, M8's table, the simulation of M8 by C04 (`Sim.v`) |
| `tools/` | | `winidle.py` (Windows Idle-priority wrapper), `split_generated.py` (see below) |

`tools/split_generated.py SRC DST` writes a copy of the tree in which each large generated file `X.v` is split into
parts `X_p00.v`, `X_p01.v`, ... that compile in parallel. `X.v` itself becomes `Require Export` of its parts. Every
lemma keeps its statement and proof, and no other file changes. The split tree has 202 files. Its longest dependency
chain is about 1/5 of the unsplit one, so it builds much faster with 8 or more cores (see the notes).
