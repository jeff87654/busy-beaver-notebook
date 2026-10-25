# Checking the M8 proof with one command

`verify.sh` builds, from a clean checkout of this repository, everything that `../Statement.v` depends on:

* busycoq at the pinned commit;
* the C04 development (`BB9/verify_c04`);
* the previous BB(8) entry (`BB8/verify`, needed for the comparison);
* the M8 layer (`BB8/verify_m8`).

It then checks three things:

1. **Audit.** Every `Theorem` of `Statement.v` (currently 12) goes into one tuple, and `Print Assumptions` on that
   tuple must say `Closed under the global context`: no axioms, no admitted lemmas, no parameters. The audit file is
   written by `verify.sh`, from the theorem names it finds in `Statement.v`; the repository's `probe.v` files are not
   used.
2. **coqchk**, Coq's independent kernel checker, re-checks `M8.Statement` and, recursively, every library it loads.
   It must accept everything and report no type-in-type, no unsafe fixpoints and no assumed positivity.
3. **The axioms coqchk lists.** coqchk's `Axioms:` list covers the whole loaded environment, not one theorem: every
   axiom *declared* in any loaded library, used or not. busycoq loads exactly four, and the audit in step 1 shows that
   the theorems use none of them:

   | axiom | declared by |
   |---|---|
   | `BusyCoq.LibTactics.inj_pair2` | busycoq's `LibTactics.v` (an `Axiom`) |
   | `Coq.Logic.ProofIrrelevance.proof_irrelevance` | stdlib; `LibTactics.v` requires `Coq.Logic.ProofIrrelevance` |
   | `Coq.Logic.Eqdep.Eq_rect_eq.eq_rect_eq` | stdlib; `LibTactics.v` loads `Coq.Program.Equality` (→ JMeq → Eqdep) |
   | `Coq.Logic.FunctionalExtensionality.functional_extensionality_dep` | stdlib; busycoq's `Flip.v` imports it |

   Any other declared axiom fails the check.

The summary prints `VERIFY: PASS`, the theorem names, and the SHA-256 of `Statement.v` and `Defs.v`. The exit status
is 0 only on PASS. What a reader has to trust is `Statement.v`, `Defs.v`, busycoq's `TM.v` and Coq (see
`../README.md`).

## Run

From this directory (`BB8/verify_m8/easy/`):

    ./verify.sh                  # Linux/macOS: Coq 8.20.1, git, make (optional), bash >= 4.4
    ./verify.sh -j 16 --split    # many cores: split the big generated files first (needs python3)

With Docker, from the repository root:

    docker build -f BB8/verify_m8/easy/Dockerfile -t m8-verify .
    docker run --rm m8-verify ./verify.sh -j 8 --split

On Windows (Coq Platform 8.20~2025.01 + Git for Windows, in Git Bash; there is no `make`, so the built-in scheduler
on `coqdep`'s graph is used). `tools/winidle.py` runs every coqc at Idle priority with a memory cap and logs PIDs
and peaks:

    COQBIN=/c/Coq-Platform~8.20~2025.01/bin/ COQC_WRAPPER="python tools/winidle.py" ./verify.sh -j 4

Other options:

* `--no-coqchk` skips step 2;
* `--resume` continues an interrupted build (`.vo` files newer than their `.v` are kept);
* `BUSYCOQ=/path/to/busycoq/verify` uses an existing checkout instead of cloning one.

The build happens in a copy, `_verify/tree/`, so the repository is never modified. Logs go to `_verify/`.

`--split` runs `tools/split_generated.py` on that copy. The 15 largest generated files (`G_sub2`, `K_e1`, ...)
become 142 parts that compile in parallel. Each `X.v` becomes `Require Export` of its parts. The lemmas, their
statements and proofs are unchanged, and no other file changes. The longest dependency chain drops from about
7,900 s to about 1,600 s of coqc time (measured per-file times; shared machine at Idle priority).

## Time and memory

Measured on a shared 16-core Windows laptop, every coqc at Idle priority, J = 4, `--split`. The other agents' load
made per-file times about 1.6x those of an earlier unsplit build on the same machine.

| step | wall time |
|---|---|
| build, 202 files of the C04 tree + M8 layer (47,140 coqc-seconds) | about 3.5 h |
| audit (Print Assumptions on all theorems) | 216 s |
| coqchk on everything | 2,192 s (37 min) |

Peak memory is about 1 GB per coqc and 1.05 GB for coqchk. On a GitHub runner (4 vCPU, J = 4) the unsplit C04 tree
took about 1 h 32 min. Simulated schedules with the measured per-file times (shared machine):

| J | unsplit | `--split` |
|---|---|---|
| 4 | 2.2 h | 2.1 h |
| 8 | 2.2 h | 1.1 h |
| 16 | 2.2 h | 0.7 h |
| 32 | 2.2 h | 0.45 h |

A dedicated machine is about 2.5x faster than these numbers.
