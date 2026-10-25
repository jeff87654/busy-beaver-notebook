# F2 tape encoding (proto2)

Alphabet {0,1}, blank 0. Token code t = run 1^(t+1) followed by ONE 0.
Codes: 0 END, 1 el, 2 eq, 3 im, 4 n, 5 al, 6+i v_i.
Wff = postfix token list closed by END.  Binder order changed to
`ph x al` (variable token immediately before `al`) so GEN is an append
(spec order `x ph al` would need an insertion at the wff front).
Atoms: `x y el`, `x y eq`.

Tape (left to right):

    1 IP 1 | gap 0^>=3 | P | Z1 | X | Z2 | S | blank

* P  persistent proof text (enumerated by next-proof), token block.
* Z1 zero run >=2 (grows when fetch zeroes the front of X).
* X  working copy of the proof: ac p1 p2 p3 ac p1 p2 p3 ... TERM.
     ac = one token (dispatched by decnz-front, leaves a run-1 residue);
     p_i = wffs.  TERM = terminator step appended by next-proof; never
     consumed, so X is never empty while S is in use.
* Z2 exactly "00" (X's last separator + one extra 0).
* S  stack: BASE token (run 2) then wffs; top = rightmost; the top wff
     may be "open" (no END yet) while it is being built.
* Blocks P, X, S contain no "00"; a zero run >=2 is a region separator.
  Exactly one transient marker (zero run) exists inside a block while a
  copy/compare gadget runs; it is removed before the gadget returns.

Gadget entry: head on first gap cell, entry state = op name.
Gadget exit: head back on same cell, state RET (or RET.f = flag/break),
where Wade's framework (5.root / break.k) takes over.

## Soundness subtleties (corrected)

1. DET in this prototype: on mismatch it DELETES both MAJOR and PH (sound:
   theorems are only discarded); on stack underflow it is a no-op. It never
   parses PH/PS; it checks MAJOR == PS ++ PH ++ [im] literally (im arg-reversed).
2. If every stack entry is well-formed, a literal DET match yields a wf PS and
   is ordinary modus ponens: the split of "Y Z" into two wffs is unique.
   (Postfix is suffix-free but not prefix-free, hence the arg-reversed im.)
3. OPEN RISK: malformed parameters. The enumerator produces arbitrary token
   strings, and axiom instantiation by concatenation with a non-wff ph can give
   a string that is a well-formed wff with an UNINTENDED (possibly false)
   parse; junk theorems (e.g. the empty string) can also combine under literal
   DET into wf results. Not proven harmless. Fixes: (a) a wf-check gadget on
   formula params plus a single-var-token check on variable params (not built;
   est. 30-40 states), or (b) Metamath-style syntax steps that build params on
   the stack, wf by construction.
4. The empty wff must never be a theorem; BASE is a run-2 token detected as
   "run 2 preceded by 00" (POP/DET guard this).
5. GEN appends a fixed var token then al; no renaming, so no capture.
