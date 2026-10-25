# How the BB(7) champion was discovered — 2026-09-26 research

The 2025 BB(7) champion was found by enumeration and subsequent analysis. Its history is therefore a concrete reason to try a broad, filtered BB(8) enumeration rather than only mutate an already understood champion.

## Primary links

- mxdys's actual C++ enumerator: https://github.com/ccz181078/TM
- Direct source: https://raw.githubusercontent.com/ccz181078/TM/main/main.cpp
- Shawn and Terry Ligocki's filtering and accelerated simulation tools: https://github.com/sligocki/busy-beaver
- Exact Kropitz discovery message linked by the machine article: https://discord.com/channels/960643023006490684/1369339127652159509/1370678203395604562
- Ligocki's machine analysis: https://wiki.bbchallenge.org/wiki/1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RZ0LC_1RG1LD_0RG0RF
- Community enumeration history: https://wiki.bbchallenge.org/wiki/BB(7)

## Discovery sequence

The BB(7) community history says mxdys released the enumerator in May 2025, partitioned into one million jobs. Typical jobs took about two minutes and retained around 100 unresolved machines. Further filtering found three tetrational champions within three days. Kropitz subsequently found the present champion in job 243308. The individual machine page dates his discovery to May 10 and Ligocki's analysis to May 13.

The record was not obtained by simulating its eventual runtime directly. Enumeration produced a candidate, and a mathematical recurrence analysis established the enormous eventual output. I could not read the linked Discord message through the web tool: it exposes only a JavaScript-required page. Thus the exact visual or programmatic feature Kropitz personally used to select this candidate from its holdout file remains unverified here.

## Reproducing the route

The mxdys repository's README gives:

    make
    ./main.exe enum 243308

The general form is `enum l r`; it emits a separate holdouts_i.txt per job. Running the seven-state discovery job first provides a valuable integration check: a faithful historical-compatible enumeration should retain the champion or an equivalent representative. Record the exact source commit because changing enumeration code may change job IDs.

For eight states the current source's domain block can be copied with N_STATE = 8, N_CHAR = 2, log2_N_STATE = 3, log2_N_CHAR = 1, and chr_t = bool. This is a proposed adaptation, not a claim that the original source ships a tested BB8 configuration. The collaborating implementation agent is inspecting the code for additional assumptions.

The original job sizes are far too coarse for an immediate BB8 experiment. A bounded pilot should retain unresolved partial machines and preserve whether each record still has undefined transitions. An unresolved partial transition table is a family awaiting more enumeration; treating every undefined entry as a final halt can lose the intended search branch.

## Second-stage tools

The Ligocki repository describes Code/Enumerate.py as its main batch tool. It generates tree-normal-form machines and/or filters an input list using Reverse_Engineer, Lin_Recur, CTL, and Quick_Sim. It supports text tables as input, with richer protobuf records as output.

Code/Quick_Sim.py uses block and backsymbol macro machines, tape compression, and an automatic rule prover. The recursive option enables second-level proofs. Disabling step calculation can make huge-number analysis cheaper while preserving the distinction between halting, proven infinite, and unresolved. Code/IO_Categorize.py separates those outcomes; Code/TM_Analyze.py summarizes them.

The BB(6) community page reports that the BB(7) second-stage runs used `--max-loops=100_000 --block-mult=2 --time=30 --save-freq=100` (https://wiki.bbchallenge.org/wiki/BB(6)). These historical settings are useful starting points, not hardware-independent performance promises. Current command help should be checked against the actual checked-out version.

## What this changes in our search

Finite raw-runtime leaderboards reward easy-to-simulate machines and do not meaningfully measure the champion's growth class. A discovery-oriented pipeline should keep hard holdouts, remove proven nonhalters with sound deciders, apply stronger symbolic acceleration, and inspect any newly discovered terminating recurrences. An op-limit result is a lead, not a score or a proof of halting.
