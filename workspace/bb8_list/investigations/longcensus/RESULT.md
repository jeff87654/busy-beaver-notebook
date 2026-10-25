# Long-census sample (2026-10-07)

Question: do slow start-ups hide digit-list machines from the regular scans (census 5e6 steps)?

Sample: 1,000 random holdouts from all 1,546,542 in the 11 BB(8) jobs (`sample_all.txt`, seed 20261007), excluding
machines already flagged by either scan. dlscan2 at census 5e8 (100x, 4 Idle parts, `long_*.tsv`) and at 5e6
(`base.tsv`), probes 20,000 steps in both.

Result: **0 digit-list grades at either census** (no CHAMPION / NOBOUNDARY / R4-SOME / CHECK / HALT-SOME / HALT?).
The longer census only finds more plain halters (123 halt within 5e8 steps, against 66 within 5e6).

Reading: no evidence that long start-ups hide a COMMON class (rule of three: a class hidden this way is below ~0.3% of
holdouts with 95% confidence). It cannot rule out a RARE one: genuine digit-list machines are ~2e-5 of holdouts (about
30 in 1.55M), far below what a 1,000-machine sample can see. Ruling that out needs the full re-scan (~850 CPU-h) or a
much larger sample; not worth it on this evidence alone.
