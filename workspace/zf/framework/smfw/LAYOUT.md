# SMFW B2: concrete tape layout, conventions, divergences

Deliverable B2 of `../SM_SPEC.md`: the tape-level primitives of the string-stack machine as
hand-written 2-symbol TM fragments, unit-tested against `../sm/sm_abstract.py`. Everything runs
with `python -I`; nothing outside `smfw/` is touched.

## Concrete orientation (SM_SPEC section 5, mirrored)

Written left-to-right, head positions increasing to the right:

    ... 0^inf  [D]  0^g0  M  <P><chain>  0^GIN  [N]  0^inf

* `D` = the data region. Its FREE end is on the LEFT (positions decreasing), away from the IP.
* `M` = the IP marker (a lone 1), PINNED at `MK` (= 41 in `codec.py`). For B2 the IP bit string `P`
  and the chain ones are empty, so a leaf is entered with the head on the first chain-one cell `MK+1`
  (matching Wade's entry convention).
* `N` = the proof-candidate counter, on the OPPOSITE side of the IP from `D`, at `MK+GIN`.
* `g0` (= GAP_DI = 40) separates `D`'s right edge from `M`; `GIN` (= 60) separates `M` from `N`.

### D encoding

`D = A  (00)  B`,  `A = T_1 .. T_m` (theorem stack, `T_m` = top),  `B = P_1 .. P_k  W  c`.

* A run of `n` ones encodes: theorem separator `n=1`; param separator `n=2`; token value `n=v`
  (`e=3 ==4 ->=5 ~=6 A=7 v_i=8+i`); counter `c = 1^(c'+3)`. Each wff = a separator run then its
  token runs. Runs are separated by a single `0`; the `A|B` boundary is a double `0`.
* `c` is the LAST (right-most) run of `D`, adjacent to the `0^g0` gap. `A` is at the free (left) end.
  With `A` empty the `00` boundary merges with the gap (D = B).
* **Invariant we enforce:** inside `D` the longest 0-run is 2 (the boundary); every other gap is a
  single 0. This makes the `0^g0` gap an unambiguous sentinel for the shared return scanners
  (`ret.adv.*`, `ret.zero.*`), which scan from inside `D` toward `M`, detect the first 0-run of
  length >= 3 (the gap), skip to `M`, erase it and fall into `6.break.0` / `6.break.1` exactly as
  Wade's `2.ret1`/`2.ret2` do. RB's data is on the N side, so it uses mirror-image left-scanning
  returns (`rb.ret.*`).

### N encoding (RB)

`N = [remaining: (1 b 0)*] [sentinel 111] [placed: (1 b 0)*] 0^inf`. RB finds the first run right of
the gap: `111` => END; else reads `b`, erases that digit, appends `1 b 0` to the first empty slot of
the placed block, and branches (bit 1 -> adv/`6.break.0`, bit 0 -> zero/`6.break.1`). On END it goes
left into `D`, erases `B`, writes a fresh `c = 111` next to the `00` boundary, erases the rest, and
falls into `5.root` (= restart main). N-rotation was verified independently (0 mismatches / 600 cases).

## Worked example

Abstract state `A=[(~ A v0 ~ = v0 v0)]` (= `(6,7,8,6,4,8,8)`), `B=[]`, `c'=0`, so D = the one
theorem then `00` then `c=111`. Runs of `D`, free end (left) first:

    T_1: sep 1 | A=7 | v0=8 | ~=6 | ==4 | v0=8 | v0=8      boundary: 00      c=111

    1 0 1111111 0 11111111 0 111111 0 1111 0 11111111 0 11111111 0 0 111   0^40  1(=M)  0^60  111

Head enters a D-side op on the first chain-one cell `MK+1` (value 0, just right of `M`).

## Divergences from SM_SPEC / sm_abstract (noted per the task)

1. **Growth consumes the IP-side gap, not the free end.** Appends (PUSH/APP1/NEW*/INCC) extend `c`
   (a small run) rightward into `0^g0`, keeping `M` pinned and the scanners' sentinel simple. SM_SPEC
   intends growth at the free (left) end so the IP gap only grows. The switch is mechanical (mirror
   the insert direction); B2 does not model gap safety (that is B3 / section-5 simulation). `codec.py`
   uses a wide `g0=40` so single ops never exhaust it.
2. **Boot stack.** SM_SPEC's boot writes an EMPTY stack (`D = 00 + c=111`); `sm_abstract` instead boots
   `A=[BOOT_THEOREM]` (B7 instance) to keep the stack non-empty for DUPT. `frag_boot.tm` follows the
   SM_SPEC text (empty A/B, c'=0, N empty); integration may prepend BOOT_THEOREM.
3. **Boot gap.** `frag_boot.tm` writes `g0=5` (minimal for the scanners); `g0>=20` is obtained by
   lengthening the two move-chains and is a measured integration parameter, not a correctness issue.
4. **Exit = `6.break.0` / `6.break.1` / `5.root` / undefined(=halt).** B2 is the data side; the IP
   arithmetic behind those labels is B3's. The test simulator (`sim.py`) treats them as sinks and
   reports the outcome (adv / zero / end / halt). CHECK halts via an undefined transition (SM_SPEC:
   halt = undefined transition).

See `COUNTS.md` for state counts and implementation status.
