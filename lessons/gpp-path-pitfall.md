---
name: gpp-path-pitfall
description: "compiling C++ tools on this machine: g++ by full path fails silently (exit 1, no output); put C:\\msys64\\ucrt64\\bin on PATH first"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-18T22:41:10.030Z
---

The MSYS2 compiler is C:\msys64\ucrt64\bin\g++.exe (gcc 16.1). Calling it by full path from Bash/PowerShell exits 1 with
no diagnostics because cc1plus.exe cannot find its DLLs (gmp/mpfr/isl/zlib) unless the bin dir is on PATH.

**How to apply:** `export PATH=/c/msys64/ucrt64/bin:$PATH && g++ -O2 -static -o x.exe x.cpp` (Bash). Not a sandbox issue
(fails the same with the sandbox disabled). Also: subprocess.Popen on Windows needs an absolute exe path (no "tools/x.exe").
Related: [[kill-only-own-pids]] (launch via a Popen driver that records PIDs).
