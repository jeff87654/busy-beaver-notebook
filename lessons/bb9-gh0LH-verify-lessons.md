---
name: bb9-gh0LH-verify-lessons
description: Lessons from verifying the 9-state G/H-swap redirect (---0LH); representatives mod 2520 are 2-adically unfaithful; tools in halt_redirect/ghv
metadata:
  type: project
---
2026-10-08: the G/H-swap 9-state candidate `..._0RG1LD_1RH1LG_1LC0RG_---0LH` halts after (77B+413)/5 champion clears. The score is about f_(m0+1), with m0 = (24B+191)/5. It is likely below the F/H three-cycle sibling. Report: halt_redirect/gh0LH_verify.md. See also [[bb8-champion-subtree-lead]].

Lessons:
- **Huge-value stages can halve tokens** (coefficients 1/2, 3/2, 7/4), so the 2-adic digits matter.
  - Towers are -6 mod 2^huge. Track the exact 2-adic part, as hv2.py does.
  - Representatives mod 2520 match only mod 8.
- **The end game depends on b mod 10 here.** The real B behaves like b = 6 mod 10 with b >= 16.
  - b = 1 mod 10 rebuilds a list of length about cR, giving a second round.
  - Pick representatives in the real class modulo every period remainder, for example D9 count mod 8 and zeros mod 6 or 12.
- **Tools:** ghv/ksim6.cpp is a block-6 chain simulator, about 10-100x faster than kst3. Pre-check the word end before expanding the whole tape.
  ghv/ghf8.py is an accelerated follower with groups, huge counts and affine periods.
- **Process hygiene:** on this shared PC, Idle processes starve. Killing a Python follower leaves its simulator child running, so kill orphans.
