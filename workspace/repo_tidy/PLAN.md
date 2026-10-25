# repo-tidy plan (branch repo-tidy, worktree C:\Users\jeffr\Downloads\repotidy_wt, from origin/main 78bd08e)

## Findings that shape the plan
- Every superseded entry except one is a proof base or is CI-built:
  - BB8/verify (champ35) is loaded by BB8/verify_m8 (Beats8.v, probe.v; BB8V=../verify) and has CI job bb8.
  - BB9/verify_fw2/multifile is copied byte-for-byte into BB9/verify_c04/lib (CI `cmp` step); CI job bb9-fw2.
  - BB9/verify_c04 is the proof base of verify_m8, verify_f3, verify_c7 (port_check.sh, -Q paths, CI filters).
  - BB9/verify_f3 (after PR #30) is the proof base of verify_c7 (CI filter lists verify_f3/lib, score, dev/Base.v).
  - Only BB9/verify + the 2026-10-07 BB9 record .txt are referenced by nothing at build time (fw2 stage 2 has copies).
- External links (wiki, issues) point at the current paths.
=> No directory moves. Superseded entries stay where they are; their status is shown by per-directory
   README.md indexes, a top-level "Superseded entries" table, and a status banner at the top of each write-up.
   (Option for the user: move BB9/verify + its .txt into BB9/superseded/ later; it is the only safe candidate.)

## Changes
1. README.md rewritten (~120 lines instead of 261):
   - one-paragraph intro + CI badge;
   - CHAMPIONS table: level, nickname + machine string linked to its write-up, proved headline bound
     (exact Coq statement wording; paper-only claims marked), main theorem names, verification (CI job / local
     build, no axioms), date, credit;
   - CONSISTENCY MACHINES table: ZF/ZFC 253 (mira-emmy, reduction of Mira-Cult's 254), 254 (Mira-Cult),
     ZFC+GU 296, our 335 (ZFC with Reg) line, PA 238 (mira-emmy); theorem names;
   - SUPERSEDED / PROOF-BASE table: machine, what superseded it, why its files remain;
   - Layout: one line per directory; conventions (σ, machine-string format, f_α definitions, busycoq pin,
     how CI runs); short per-entry notes linking to BBn/README.md and the write-ups.
2. New per-directory index files BB8/README.md, BB9/README.md, BB10/README.md, BB12/README.md, BB13/README.md,
   BB14/README.md, BB43/README.md, PA/README.md: current entry first (string, bound, files, CI job), then
   "Superseded / proof bases", then tools. ZF/README.md already opens with the current machines; add a short
   index table at its top only.
3. Write-up convention: title "# <nick>: a k-state machine with <headline bound>" (retitle n1, T12a, M13, M14,
   fw2 pages that lack the nickname), machine string as the first code block, then a one-line status banner
   ("> **Status:** BB(n) entry of this repository" or "> **Superseded** by X (date); kept because ...").
   Banner added to the 2026-10-07 BB9 record .txt (it has none). No other content changes in write-ups
   except the stale fixes below.
4. Stale statements to fix (each listed in the PR):
   - README / BB8 write-up / C04 write-up / verify_m8 README: internal agent names (bb8-resid, m8-coq,
     c04-fable, c04-upper, c04-coq, c04-coq2, c04-k31, c04-bound, c04-fgh) -> neutral wording.
   - BB10 + BB12 + BB10/screen pages call champ35 "the BB(8) record": add a note that this is the BB(8)
     entry until 2026-10-18, now superseded by M8 (text otherwise unchanged).
   - C04 banner "a 9-state record must beat M8" -> point to the current BB(9) entry (after C7 merges).
   - coq.yml comments: bb9-c04 job called "the BB(9) entry"; f3 job (after #30) "the BB(9) entry"; zf job
     comment lists 3 machines, matrix has 5; bb8-m8 comment "55 files" vs 56 checked. Comment-only edits; they
     put .github/ in the diff, so the PR runs every job (full CI) -- acceptable, it also validates paths.
   - anything else found while writing the tables (each theorem name checked against the .v files).
5. Tools (kept in C:\Users\jeffr\Downloads\bb8\repo_tidy, not committed unless useful):
   linkcheck.py (every relative link/image in every .md resolves, incl. #anchors to headings),
   cicheck.py (every working-directory, path, glob and filter in coq.yml/zf253.yml matches existing files).

## Order
A. Now: per-directory READMEs for BB8, BB10, BB12, BB13, BB14, BB43, PA; write-up titles/banners; stale fixes
   outside BB9; README skeleton; tools.
B. After the lead says PR #30 and the C7 PR are merged: rebase onto origin/main, fill BB9 row + BB9/README.md
   from the merged files (theorem names from c7/Statement.v), fix coq.yml comments on the merged text,
   run linkcheck + cicheck, push, open PR (not merged), watch CI.
