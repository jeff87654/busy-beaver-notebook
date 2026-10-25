---
name: wiki-champion-rows-convention
description: The BB wiki champion table blanks rows n dominated by a smaller-n machine (11-13 blanked after n1 at 10); H14 proof not needed
metadata:
  type: reference
---
The bbchallenge wiki champion table leaves a row blank when a machine with fewer states already beats that n's champion (by monotonicity: add unreachable states). After we uploaded n1 (BB(10), f_(omega+1)), rows 11-13 were blanked (user, 2026-10-10).

**How to apply:** a proved T12a (12 states, f_(omega+1)^2) takes row 12 and should blank 13-15 by published bounds. As of 2026-10-11 the wiki has BB14 > f_(w+1)(f_w^4(f_7(3))), BB15 > f_(w+1)^2(10^10^57) and BB16 > f_(w+1)^3(f_w^2(f_6^2(3))), so row 16 is NOT dominated. (An earlier note wrongly called BB14-16 all f_(w+1).) So H14 (14 states, same class) needs no Coq proof unless T12a's proof fails. An f_(omega+2) machine at n <= 16 blanks row 17/18 only if it beats the BB17/BB18 champions' actual values (d = 6 / 8 layers), not just their class. See [[w2-12state-search]], [[bb17-bb18-champion-anatomy]].
