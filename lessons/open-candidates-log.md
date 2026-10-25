---
name: open-candidates-log
description: "User wants a durable log of potentially record-beating machines we can't settle yet: bb8_list/investigations/OPEN_CANDIDATES.txt"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 0123e68f-85a6-4951-813e-1a4014f110cc
  modified: 2026-10-18T22:05:29.392Z
---

Keep every potentially record-beating machine that we can't currently settle in `bb8_list/investigations/OPEN_CANDIDATES.txt`. That includes ones that can't be certified (class-dependent, Collatz-hard) and ones that are undecided. Each entry needs the machine, the bar it might beat, its status, the exact obstacle, and where its data lives. Settled entries move to a SETTLED section; nothing is deleted.

**Why:** the user said (2026-10-18) "let's keep a log of potentially record beating machines that we can't solve right now. We might have more luck in the future." C04 was once dismissed as "Collatz-hard" and later became a record ([[c04-bb9-candidate]]).

**How to apply:**
- Tell search and analysis agents in their prompts to append unsolved candidates there. The file is .txt so subagents can append it with a shell heredoc.
- Update it when leads are settled.
- Check it when starting new searches or when new tools appear.
- Related: [[m8-bb8-c04-collapse]].
