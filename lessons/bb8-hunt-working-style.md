---
name: bb8-hunt-working-style
description: "How the user likes the BB(8) search work run: series with lessons learned, cheap automation before tokens, verified results"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5dec1c71-d48e-4f98-ab96-c3f375bdf014
  modified: 2026-09-28T13:52:57.615Z
---

- **Run investigations in series,** feeding each one's lessons and tools into the next to cut cost. This worked: in the neighbor search, one family investigation's tools (kfit.py and gen_kcoq*.py) settled 10 of the next 16 machines with no agent at all.
- **Automate cheaply before spending tokens.** The user explicitly prefers trading some CPU for tokens, within reason: the mxdys pre-filter, dedup, and proof generators.
- **Hold modifications of known machines to a high bar.** The user was skeptical of that approach, since BB(7) records came fresh from enumeration. They accepted the Ackermann-counter neighbor search only because that structure is record-class.

**Why:** the user said to take the families in series so later investigations get cheaper, and welcomed "a cheaper automated proof check ... as long as it doesn't load the CPU too much".
**How to apply:**
- Reuse existing generators and reports in bb8_list/investigations before launching new subagents.
- Report the token cost of each investigation.
- Keep agents at model "opus"; see the user's global CLAUDE.md.

Related: [[bb8-hunt-operating-policy]].
