# Investigation brief (template for subagents)

You are analyzing one Turing machine flagged by our busy-beaver candidate pipeline. Determine its
long-term behavior as rigorously as you can, and report what is proved separately from what is conjectured.

## Machine
- Machine: `{MACHINE}` (standard text format; `---` = undefined transition, treated as the halt)
- States: {STATES}. Source: {SOURCE}
- Growth data from our pipeline (Ligocki Quick_Sim, `--recursive`, CPU-second budgets):
  {GROWTH}
- Calibration: the BB(7) champion `1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF` scores
  1,872 / 6,850 / 14,397 digits at 2 / 10 / 40 CPU-s. Its digits per loop rise from 0.84 to 2.26 toward Quick_Sim's ~3.01 cap:
  general rules are applied at most --max-num-reps = 10 times per loop.
  - This "doubling-class" signature does NOT imply halting or nested growth.
  - The control investigation `bb8_list\investigations\bb7_control_16582.md` proved a doubling-class BB(7) holdout
    nonhalting. Read it first: it shows a working method, including a small symbolic prover
    (`bb7_control_16582\symsim.py`) that you may adapt.
  - Plain exponential growers keep a flat ~0.01-0.02 digits per loop.
  The champion halts with sigma > 2↑¹¹2↑¹¹3. Ligocki's analysis uses configurations B(a; b1..bk) with rules
  B(a; b+1,...) -> B(2a+4; b,...) and B(a; 0^k, 0, n+1, ...) -> B(0; 0^k, a+2, n, ...)
  (see https://wiki.bbchallenge.org/wiki/1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF).

## Tools (Windows; project root `C:\Users\jeffr\Downloads\bb8`)
- Python with dependencies: `third_party\venv311\Scripts\python.exe`
- Ligocki's tools (unmodified): `third_party\ligocki\Code\` (Quick_Sim.py, Macro/, etc.).
  Run Quick_Sim from that directory; `python Quick_Sim.py --help` lists options.
  Verbose output or the prover's rule printing shows the proven rules.
- Wrapper with structured output: `ligocki_runner.py --machine M --recursive --max-loops N --sim-time T --output out.json`
- Exact literal simulator (no acceleration) for checking small cases: `sim.py`; a JS literal simulator exists in `audit_verify.js`.
- Web: the bbchallenge wiki (wiki.bbchallenge.org) for known machines and conventions.

## What to do
1. Find the machine's repeating configuration family. Use Quick_Sim's proven rules plus your own tape
   inspection at intermediate points.
2. Derive the recurrence on the family's parameters. Check each rule against exact literal simulation on small
   parameter values.
3. Decide the long-term behavior:
   - Halts: give sigma and steps, or bounds in Knuth up-arrow / 10↑↑x notation.
   - Provably never halts: give the invariant.
   - Otherwise say "unresolved" and name the precise open condition.
4. Compare with the relevant record. For BB(8), anything must beat 2↑¹¹2↑¹¹3 to matter; also note whether the
   machine is merely a trivial variant of a known machine.
5. Work alone. Do not spawn subagents, teammates or helper sessions; if something is out of scope, list it
   under open questions. Stop only processes you started, by PID. Never kill by image name (e.g. all
   `coqc.exe`) and never change other processes' priorities.
6. Keep compute polite: this PC is shared. Before your final message, stop every background process or shell job you started. Keep single runs to a few CPU-minutes, and run long simulations at Idle
   priority (PowerShell `Start-Process ... -PassThru` then `.PriorityClass = 'Idle'`).

## Formal proof (required for a non-halting verdict)
- If you conclude the machine never halts, also write a machine-checked busycoq proof in
  `bb8_list\proofs\` following `bb8_list\proofs\README.md`, then run `python check.py <File.v>` there.
  - A verdict of "proved" requires a PASS.
  - If you cannot finish the formal proof, commit the partial file with a clear `(* TODO *)` list, and report
    the verdict as "strong evidence", not "proved".
  - Building is slow (~10 s per file); do not rebuild upstream busycoq needlessly.
- For a halting verdict, a Coq proof of `Theorem halt : halts tm c0.` is strongly preferred (it is feasible: see `proofs/BB8_76450_1RB1LG.v`). `check.py` accepts it. The sigma estimate still needs exact literal checks of every rule.

## Output
- Write a report to `bb8_list\investigations\{SLUG}.md`: verdict, confidence (proved (Coq PASS) / strong evidence /
  conjecture), configuration family, rules with verification, recurrence, score estimate, reproduction
  commands, and open questions. Put scratch scripts in `bb8_list\investigations\{SLUG}\`.
  Write the report with a Bash heredoc, because the Write tool refuses report `.md` files from subagents.
- Apart from your investigation files, the only permitted changes are:
  - creating your proof file (and its build outputs) in `bb8_list\proofs\`;
  - adding one row to the "Proved" table in `bb8_list\proofs\README.md` after a PASS.
  Do not modify any other files in the project.
- Final message: at most 250 words, with the verdict first.
