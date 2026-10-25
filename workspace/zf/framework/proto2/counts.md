# F2 measured state counts (proto2) -- updated as gadgets pass tests

shared back-to-IP chains (plain + flagged): 18
NEWTOK 8 (300/300), UNIT 9 (300/300)
DECNZ(front, = dispatch on ac) 6 (600/600), DELWFF(front) 7 (300/300), POP 21 (300/300)
COPY_i (i=1..3) 56 total: core 35 + skip chain 9 + 3 walk-outs x4 (900/900)
Design change for DET: im stored with swapped args ("B A im" = A->B), i.e.
reversed-prefix order, so DET compares PH against MAJOR's *suffix* and the
consumed region ends up at the right (no hole compaction).
DET (compare-and-detach, fail => delete both, underflow => no-op) 69 own
  states + reuses POP's left-scan (3000/3000 random tests: success, near-miss,
  wrong main connective, PH too long, run-2 tokens next to BASE, under-full stack)
GEN 27 (300/300), EQLEN/B6a-core 16 incl 2 sinks = 14 real (64/64 exhaustive)
INC odometer add-one core 8 (LSD +1; full carry/normalize/grow est +18 => ~26)

MEASURED GADGET LIBRARY (deduped shared walk-out/walk-back): 221 distinct states
  (DET tested together with POP; COPY1/2/3 share one 56-state body.)
Per gadget: NEWTOK 8, UNIT 9, DECNZ 6, DELWFF 7, POP 21, COPY 56,
  DET 90, GEN 27 + shared back-chains 18.

Axiom postfix sizes (axcount.py, primitives im/neg/all + atoms; ph/ps/ch=copy):
  total literal tokens 263, param copies 23, over 16 axiom bodies.
  biggest: REP 56, INF 45, EXT 23, UNI 23, B6a 21, POW 19.

WHOLE-MACHINE ESTIMATE vs 393
-----------------------------
Framework (engine) = boot 9 + measured gadget lib 221 + NEXTPROOF odometer ~26
  + fetch/regenerate-X block copy ~25 + B6a (EQLEN) 14 + proof-step dispatch ~15
  = ~310 states.  (DET 90 and COPY 56 dominate; neither is tuned.)

Program cost depends on how axiom bodies are stored:
 (A) compile each axiom into a push-sequence (tokens become PROGRAM/DAG nodes):
     263 tok*0.6 + 23 copies*0.6 + ~36 control = 158+14+36 = ~208.
     TOTAL ~310+208 = ~518  >> 393  (WORSE).
 (B) store axiom bodies as postfix token TEMPLATES as DATA on the tape (as Wade
     stores Cantor integers) + one generic instantiate-with-subst gadget (~40):
     program control only ~45; framework ~310+40 = ~350.
     TOTAL ~395  ~= 393  (BREAK-EVEN).

Conclusion: tape-native postfix makes per-step logic gadgets concrete and cheap
individually, but F2 is at best BREAK-EVEN, not a clear win, because
 - compare-and-detach (DET, 90) and parameter copy (COPY, 56) balloon;
 - proof enumeration still needs an odometer + a regenerate/copy of the working
   proof text each step (destructive gadgets force regeneration);
 - unless axiom bodies stay as tape DATA (design B), compiling 263 tokens into
   program nodes alone costs ~200 states.
Cheapest configuration found: design (B) + token code 0..9 single-0 separators,
binder stored as `ph x al` (GEN = append), im stored arg-reversed (DET detaches
at the right end, no hole compaction). Best estimate ~350-395 states.
