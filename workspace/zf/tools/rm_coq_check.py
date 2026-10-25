"""Sanity: compute the RM run in Coq (vm_compute) for N ops and compare registers with the Python RM."""
import sys, subprocess, re
sys.path.insert(0, 'tools')
from dag import extract, RM
N = int(sys.argv[1])
start, tbl, nodes, regidx = extract('ext/turing_machine_explorer/zf2.tm')
rm = RM(nodes, 'main().0', len(regidx))
for _ in range(N): rm.step(regidx)
print('python regs', rm.regs, 'P', ''.join(map(str, rm.P)))
v = f'''From ZF Require Import RM ZF2Dag.
From Coq Require Import Lists.List.
Import ListNotations.
Definition res := rm_run zf2 {N} ([], regs0).
Eval vm_compute in (match res with Some (P, R) => Some (P, map R (seq 0 11)) | None => None end).
'''
open('coq/Scratch_check.v', 'w').write(v)
r = subprocess.run([r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe', '-Q', 'coq', 'ZF', '-Q', '../third_party/busycoq/verify', 'BusyCoq', 'coq/Scratch_check.v'], capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:])
