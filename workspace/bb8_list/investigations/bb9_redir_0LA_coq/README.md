# Scratch: Coq proof for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA

Report: ../bb9_redir_0LA_coq.md. Final files: ../../proofs/BB9_redir_0LA.v (halting, check.py PASS),
../../proofs/BB9_redir_0LA_bound.v (exact score, comparison with the record formula). Notes: NOTES.md.

- gen_final.py OUT.v: whole halting proof (gen_machine.py + abstract.v.in + arith.v.in + main.v.in).
- gen_bound.py OUT.v: bound file from bound.v.in (needs machine_info.pkl written by gen_machine).
- Machine-specific shapes: common.py (KR, tok), st0.py (stage 0 start/target), p3loop3.py (stage-2 hand loop X3, E2 from st2e.py).
- handloop.py: hand-specified transfer loops; phases.py: drive/regroup; inst.py, litcheck.py: literal checks of symbolic configs.
- Literal tools: lit.py, trace0.py, trace2.py, snap.py, grid2.py (tm_old.Sim).
- coqc_idle.py (Idle compile), coqc_dev.py (adds -Q dev Dev for dev/*.v), probe_bound.v/.log (statement printout).
