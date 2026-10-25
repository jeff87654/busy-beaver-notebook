---
name: kill-only-own-pids
description: Never kill coqc/python by image name or start time; only by the PID recorded at launch (other agents share the machine)
metadata:
  node_type: memory
  type: feedback
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-18T19:05:56.857Z
---

Kill only processes you started yourself, using the PID you recorded when you launched them. Never select them by image name (coqc) or by start-time filter.

**Why:** on 2026-10-16 I killed another agent's coqc while stopping my own hung compile (broke the BB9_redir_0LA timing run). Again on 2026-10-17 I ran `taskkill` on ALL python.exe to clean up one diverging explore of mine, terminating 7 PIDs — several belonged to sibling agents (c04-upper/-fable/-sib run python tools). Several agents share this machine; killing by name hits their jobs.
Also 2026-10-18: two `python _pfx.py` explores I "killed" kept running for 13 CPU-hours each, because I had killed only their nohup/bash wrapper PIDs (Git Bash `$!` is the wrapper, and `ps` PIDs are not Windows PIDs). The lead found them.
**How to apply:** launch long jobs through a wrapper that records the PID, and kill ONLY that recorded PID on timeout. Never `taskkill`/`kill` by image name (coqc, python, pkf*) or by start-time filter, even for "stray" cleanup. For a backgrounded Python explore, capture its PID at launch so you can kill just it. Record the real child's Windows PID: look it up with Get-CimInstance Win32_Process, matching your own command line. After killing, verify it is gone the same way. The scratchpad `cq.sh` from the M11 session ([[m11-argon-bb11]]) does this for coqc.
- Incident 2026-10-18 about 22:45: c04-coq2 ran taskkill on all python.exe (7 PIDs) to stop its own diverging run. It may have killed other agents' python drivers and wrappers. The lead notified symsim, c04-sib, c04-bound and jzseed to check and restart. Spawn prompts should keep saying: look up your own PID by command line (Get-CimInstance Win32_Process), never kill by name.
