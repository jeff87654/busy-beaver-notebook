"""Rewrite ../../bb8_m7_1RB0RA_1RA0LC.md after the Opus continuation (python upd_report.py "CHECK LINE" "COMPILE TIME")."""
import sys
from pathlib import Path
REP = Path(__file__).resolve().parents[1].parent / 'bb8_m7_1RB0RA_1RA0LC.md'
old = REP.read_text(encoding='utf-8')
check_line, ctime = sys.argv[1], sys.argv[2]

def section(name):
    i = old.index('## ' + name)
    j = old.find('\n## ', i + 1)
    return old[i:j if j >= 0 else len(old)].rstrip() + '\n'

head = '''# BB(8) m7-subtree NOBOUNDARY machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF

Scratch dirs: bb8_list/investigations/bb8_m7_1RB0RA_1RA0LC/ (Sonnet investigation, tools listed at the end) and its opus/ subfolder (Opus
continuation: generators of the proof). Proof: bb8_list/proofs/BB8_m7_1RB0RA_1RA0LC.v. Investigators: Sonnet 5.5 (about 350k tokens; macro
structure, all rules checked literally, skeleton proof), then Opus 5.5 (the Coq proof).

## Verdict

**NEVER HALTS: proved (Coq, check.py PASS, no axioms).** Not a record candidate (no halt, no sigma).

    %s

(compile time %s, at Idle priority on a fully loaded PC; the generated machine-level lemmas take almost all of it.)

After the champion's first epoch the used-up list is REBUILT (neither halt nor cycler) through a fixed lifecycle of nonstandard tokens into a
STANDARD 3-token champion list, which the champion rules process again, and so on forever: the token count (left of the a-token) goes
11 -> 3 -> 3 -> ...

## The proof (Opus continuation, 2026-10-07/08)

Family (nearest-first lists, as in the sibling proof BB8_m7_1RB0RA_1RH1LG.v):
`K P11 ds a r = 0^inf 11 D(ds..) D(a) (10)^r 111001 B> 0^inf`, D(m) = (10)^m 1. Closed family with `progress_nonhalt_cond` (every state has a
successor, no ordering argument), three kinds of state:
- `Std ds a r`: the champion's family; all tokens = 1 mod 3, a = 1 mod 3, r = 2 mod 3, length ds = 11 or 3, and "a = 1 and r = 2 imply some
  token != 1" (so a used-up list always has r = 3c+5, i.e. b >= 1: it arises from R1, r -> 2r+4 >= 8). Steps: R1, R2, R3 (the champion's rules,
  context 1::l), and the used-up list (n = 11 or 3) -> `Life (7+12c) 762 2 T`, T = 3n+13 (lemmas KUSED11, KUSED3).
- `Life k a r T` = `[T, 21, 1^k, 0, 1 | a] r` with k odd, a = 0 mod 3: R1 while a >= 3; at a = 0 STAGE (k -> k-2, a := 2r+2, r := 2) or,
  at k = 1, ENDA -> `Fin (2r+2) 2 T`.
- `Fin a r T` = `[T, 20, 1 | a] r`, a = 0 mod 3: R1 while a >= 3; at a = 0 ENDB -> `Std [2r+3, 16, T] 1 2` (3 tokens, contains 16).

The used-up rebuild, for n in {3, 11}, r = 3c+5 (`KUSEDn`, composed of machine-level lemmas, waypoints found from literal traces and checked
with `python wp.py check N`):
1. `UAn`: used list -->+ Z_n(6c+10, 1), where Z_n(x, k) = B on the blank left end of `0 (01)^x 00 (101)^k (100)^(n+2) 101` (the head has
   run the whole list into this "bounce" form; the old tokens became (100)^(n+2) 101).
2. `ZRn`: Z_n(x+1, k) -->+ Z_n(x, k+2) (one bounce); `ZITn` iterates it by induction: Z_n(6c+10, 1) -->* Z_n(0, 12c+21). This loop is
   the quadratic part of the transient; the explorer cannot find it inside one exploration because x = 6c+10 is a run of 12-cell
   blocks while a round peels 2 cells, hence the explicit waypoint.
3. `UBn`: Z_n(0, 21+m) -->+ C1 = `[T+3, 1^(11+m), 2, 0, 3 | 3]` r = 2 (linear in m, for any m; used with m = 12c).
4. `C12`: C1 -->+ C2 = `[T, 21, 1^(9+m), 0, 0 | 19]` r = 2 (any leftmost token 3+x); six R1 steps (19 -> 1, r: 2 -> 380);
   `C23`: `[x, 21, 1^(9+m), 0, 0 | 1]` r = 2+3q -->+ C3 = `[x, 21, 1^(7+m), 0, 1 | 2r+2]` r = 2 (q general, used with q = 126: a = 762).
The lifecycle rules STAGE, ENDA, ENDB are stated with r = 2+3q (with r = 1 the explorer finds a halt: the residue mod 3 matters).
`init_reach`: 2117 literal steps from the blank tape to `Std (1^10 ++ [7]) 1 2` = the champion's K([2, 0^10]; 0; 0).

Generators (opus/; python = third_party/venv311/Scripts/python.exe):
- `python gen_final.py full0.v` explores and proves all 14 machine-level lemmas with mexp.py (copied from
  ../bb8_m7_1RB0RA_1RH1LG/gen/, plus an optional MEXP_TRACE progress print) and appends the hand-written glue `glue.v.in` (+ `used.v.in`);
  `python assemble.py full0.v OUT.v` re-attaches the current glue to an existing generated part; `assemble.py ... stub` replaces the
  generated lemmas by Admitted stubs to test the glue quickly (DEV ONLY, never a proof).
- `wp.py` (waypoints UA/ZR/UB/C12/C23, literal checks with `validate.reaches`), `gen_rules.py` (R1-R3), `gen_life.py` (STAGE/ENDA/ENDB),
  `tr2.py` / `ksnap.py` / `zprobe.py` (literal traces: the bounce loop, Z(0,k) -> C1 for all k >= 15).
- `bg.py` starts a command at Idle priority; `coqc_idle.py`, `check_idle.py` compile / check at Idle.

Lessons: the Sonnet macro description was exactly right; the only obstacle for automation was the quadratic bounce loop, solved by one
waypoint (Z(6c+10, 1)) and a hand-iterated round lemma, as in the sibling 1RH1LG proof (whose ZR/ZIT has the same shape: there TOK =
(100)^13 101, here (100)^(n+2) 101).
'''

body = (section('Setting and notation') + '\n' + section('Verified facts') + '\n' + section('The lifecycle for n = 3 mod 4')
        + '\n' + section('Evidence against halting'))
gap = '''## Remaining gap

None: closed by the Opus continuation above. Not needed and not checked: n = 0, 1 mod 4 and the b = 0 branch of the rebuild (the
invariant shows n stays in {11, 3} and b >= 1). Note the proof's lifecycle starts from C3 with the 762-token, so the token tables of the
Sonnet report for C1 -> C3 are now machine-checked for every b.
'''
tail = section('Comparison') + '\n' + section('Reproduction')
cost = '''## Cost
- Sonnet: about 350k tokens (60k reading the siblings and tools, 120k token-level inspection, 90k rule tables and checks, 50k lifecycle end
  and the n = 3 cycle, 30k report).
- Opus continuation: about %s tokens (reading the report and the sibling generators, waypoints of the rebuild, glue, two stub compiles and
  the final check; most of the wall time was coqc at Idle on a saturated PC).
''' % (sys.argv[3] if len(sys.argv) > 3 else '?')
REP.write_text(head % (check_line, ctime) + '\n' + body + '\n' + gap + '\n' + tail + '\n' + cost, encoding='utf-8', newline='\n')
print('wrote', REP)
