# Scratch: Coq proof for 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA (three-cycle sibling)

Report: ../bb9_redir_0LA_fh_coq.md. Final files: ../../proofs/BB9_redir_0LA_fh.v (check.py PASS),
../../proofs/BB9_redir_0LA_fh_bound.v (score, beats 0LA formula, beats the BB(9) record). Resume notes: NOTES.md.

- python gen_final_fh.py OUT.v  (whole halting proof; --dev writes only the abstract part importing Dev.M)
- python gen_machine_fh.py dev/M.v ; python mk_bound_tmpl.py ; python gen_bound_fh.py OUT.v
- coqc_idle.py / coqc_dev.py (Idle compiles), probe_fh.v / probe_fh.log (statements), endcheck.py (end vs target).
- Shapes: st0a.py hop.py st0b.py mr.py st2c.py st3e.py st3y.py st3x.py; tools: phases.py (drive, drive_peel, regroup),
  handloop.py, inst.py, litcheck.py, fhlit.py, trace0.py, trace3.py, rounddbg.py.
