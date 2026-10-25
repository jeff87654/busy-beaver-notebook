# busy-beaver-notebook

The working notes, tools and small data files behind
[jeff87654/busy-beaver](https://github.com/jeff87654/busy-beaver). That repository holds the finished results with
axiom-free Coq proofs: new lower bounds for BB(7) to BB(14) and BB(4,3), and Turing machines that halt iff ZF, ZFC,
ZFC + universes or PA is inconsistent. **This repository is the lab notebook**: plans, investigation reports,
dead ends, screening tools and lessons from about a month of searching (2026-09-26 to 2026-10-25) by AI agents.
Claude models did most of the work, and a Gemini agent called Argon worked in the same folder.

It is published mainly for **other people's AI agents**. Clone it and point your agent at [`AGENTS.md`](AGENTS.md).

> **Nothing here is verified unless the main repository says so.** The notes are unedited working documents. Many
> contain claims that were later refuted, superseded or never settled, and some reports (especially Argon's) call
> simulation results "proofs". [`STATUS.md`](STATUS.md) gives the current state and [`INDEX.md`](INDEX.md) tags every note.

## What's here

| path | contents |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Start here if you are an AI agent: reading order, conventions, trust rules, how to search this repo |
| [`METHODS.md`](METHODS.md) | How the search was run and where each record came from; the agent failure modes we hit |
| [`STATUS.md`](STATUS.md) | Verified results, routes searched and closed, refuted claims, open leads |
| [`INDEX.md`](INDEX.md), [`index.jsonl`](index.jsonl) | All 426 notes with one-line summaries and status tags |
| [`lessons/`](lessons/) | The lead agent's long-term memory: 57 short notes, one lesson each |
| [`workspace/`](workspace/) | The working folder, filtered: notes (`.md`, report `.txt`), tool source (`.py`, `.cpp`, `.rs`, `.js`, `.ps1`) and data files under 20 KB, in their original layout |
| [`DATA_MANIFEST.tsv`](DATA_MANIFEST.tsv) | The 4,522 larger data files (5.8 GB) that were left out, with sizes |

Left out: compiled binaries, Coq development files (the finished proofs are in the main repository), run logs, large
data, vendored third-party libraries, copies of other authors' unpublished material, and a few personal notes.

## Paths

The notes and scripts use the original absolute paths. To translate:

- `C:\Users\jeffr\Downloads\bb8\X` (or `/c/Users/jeffr/Downloads/bb8/X`) → `workspace/X`
- `C:\Users\jeffr\.claude\projects\...\memory\X.md` → `lessons/X.md`

Many scripts expect an executable that was built from the `.cpp`/`.rs` file next to them; build it yourself.
Some also need data files that are listed in `DATA_MANIFEST.tsv` but not included.

## License

Code (`.py`, `.cpp`, `.c`, `.h`, `.rs`, `.js`, `.ps1`) is under the [MIT License](LICENSE-CODE). Notes, lessons,
indexes and data are under [CC BY 4.0](LICENSE-DOCS). See [`LICENSE`](LICENSE).

## Credits

The search was run by the repository owner (Jeff Ketchersid) with Claude models (Anthropic) as lead and investigator
agents. Argon is a Google Gemini model the owner ran in Google's Antigravity. Notes in `workspace/` written by Argon
are mostly in Gemini's own style ("Wait: ...", "Theorem"). Work by others that the notes rely on is credited in the
main repository: the bbchallenge community (holdout lists, busycoq, deciders, the BB(7) champion analysis), Racheline,
Jacobzheng, Kropitz and Polygon (champion machines), Wade (TM compiler for the consistency machines), and Mira-Cult and
mira-emmy (the 254-, 253- and 238-state consistency machines).
