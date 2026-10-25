# Independent decider audit: last five candidates

## C03: independently proved nonhalting

The native search agent discovered a translating right-suffix recurrence. `lastfive_decider_c03_independent.py` uses its own literal parser and set-of-ones simulator. Starting from blank it verifies step 83,806, state F, head -50. It then discards every tape cell left of -54 and regards those cells as unknown, rejecting any subsequent read there. After exactly 23,636 transitions, state F and head -18 are reached, and the entire suffix starting at -22 equals the original known suffix translated right by 32 cells. The actual read/write range is [-51,159]. A separate continued simulation from the full blank-origin configuration gives the same endpoint.

Thus the result is a universal partial-configuration recurrence: the arbitrary left part cannot affect the period, and the required right suffix is reproduced. Induction proves nonhalting. This is not inference from finitely many repeated samples. The negative control placing the boundary at -50 is rejected on the unknown read of -51 at cycle step 37. Exact tape positions and results are in `lastfive_decider_c03_independent.json`.

## C13/C15: 108 new standalone CPS settings, no classification

`lastfive_decider_cps.py` ran 48 settings (24 each on representatives C13 and C15): history none, fixed lengths 1/2/4/8, and LRU; blocks 1/2/3/4; window three times the block. All 48 terminated inconclusively because the abstraction included a halting configuration.

`lastfive_decider_cps_deep.py` ran another 60 settings: histories none/2/8/LRU, blocks 6/8/12, windows 2b+1 or 3b; plus fixed histories 16/32 at blocks 8/12/16 and window 3b. Twenty-eight included abstract halting configurations; 32 reached their external six-second wall timeout. These are all inconclusive. An abstract halting configuration is not a claim that the actual blank-tape machine halts. Two workers were used, and every child process finished or was terminated by the wrapper. No portfolio process remains running.

The two JSON files preserve every exact setting and outcome, including counters when available. The first portfolio records SHA256 hashes of the unmodified upstream CPS and Turing_Machine sources. No upstream file was modified.

## Source issue and explicit local correction

In the downloaded upstream `Macro/Turing_Machine.py`, `Fixed_History_MM.get_trans_object` calls `update_history_lru` instead of the already-defined `update_history_fixed`; its `max_hist` value is ignored. Therefore upstream fixed-history parameter changes would silently repeat LRU semantics. The wrapper defines a local subclass that calls `update_history_fixed(hs, written_symbol, (output_state,written_symbol), max_hist)`. Its annotation affects only the auxiliary alphabet, never the underlying machine transition. A repeated-identical-event check distinguishes the corrected fixed history from LRU and verifies the requested history length. Results explicitly identify this derivative; the original source is preserved.

## Independent certificate checker and calibration limitation

`lastfive_decider_cps_verify.py` imports no upstream simulator or CPS implementation. From an exported finite graph it checks: zero-tail and initial-configuration inclusion; the history annotation rules; literal simulation of every window; absence of halting transitions; exact local repetition where relevant; and every continuation-edge and successor-configuration closure obligation. A success flag from the discovery engine is not accepted as evidence by itself.

No C13/C15 run produced a candidate invariant, so none was classified using this checker. Two external subprocess attempts to calibrate the engine on a one-state runaway hit ten-second timeouts during a period of tool/runtime delays. A direct execution subsequently exported a three-configuration certificate for `1RA1RA`. The independent checker and malformed-certificate controls are recorded in `lastfive_decider_cps_calibration.json`. No additional BB2 or oscillator engine calibration is claimed.

The useful new classification in this audit is C03. C13/C14 and C15/C16 remain unresolved by these tests.
