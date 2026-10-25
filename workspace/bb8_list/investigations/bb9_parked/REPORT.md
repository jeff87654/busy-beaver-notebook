# bb9_parked: n1f0 residual leads (approach #1 toward a 9-state G-beater)

The lead writes this file from the reports of agents bb9-parked (until the 2026-10-17 reboot) and bb9-parked2. The
agents' own data files hold the crash-safe state: classify_g6.tsv, classify_bigB.tsv, runs/*, pids2.txt.

## Result so far (2026-10-17)

No G candidate (G < f_(w+1)(64)). Every lead except C04 is classified:

| class | leads | evidence |
|---|---|---|
| HALT-LOW (at most 1 escalation, omega-level ~2) | C07 C09 C12 C13 C17 C19 C22 C24 C25 C26 C27 C32 N2a N2b | halt within J2-J7 in every world (fixed B=6..21, g6); N2a/N2b: 3 and 6 clears at depth 12B+4, robust for B=6..26 and R=6..302; C32 halts at J277 with 0 escalations |
| NONHALT, Ligocki Inf_Repeat | C14 C15 C18 C20 C23 C29 C31 (C05 at B=6 only; lkf runs out of memory at large B) | robust at B = 6, 2526, 5046 |
| f_(w+1)-shape loopers, slot never read | C01 C02 C03 C06 C08 C10 C11 C16 C21 C28 | rebuild every 1-2 periods; no counter; 300-400 jumps in worlds B=6..21 fixed, g6, B=2526 grow |
| no escalation (RUN-FLAT) | C30 C33-C39 | cleared list <= 35 and shrinking |
| rebuild/consume cyclers, slot never read | N1a N1b N1c N1d | tail counter t only increases; 9k-38k small-world jumps |
| OPEN | C04 | below |

## C04 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF

Notation Kt/Kg as in proofs/BB9_record_1RB0RA.v. Tools: ktr.exe (literal K-moment tracer), pkf3.exe (pkf with a
--kt start config), towermod.py, c04res.py, mkph3.py, exh3.sh.

- **B = the record's B.**
  - From blank, C04 and the record 1RB0RA_..._0LH1RZ give identical token sequences over the first 12 K-moments.
  - On 941 random digit-form configs their next K-moments agree. The only mismatches (59) are exhaustion configs, where the gadgets differ.
  - So C04 reaches Kg(0^11)[]0 B 0 with 2B+4 = 2↑^13 3. B ≡ 1 mod 5 and B ≡ 6 mod 2520.
- **P1 (exhaustion #1)**, literal for b = 0,1,2,7,100..104,616,2491:
  - Kg(0^11)[]0 b 0 ->* [0,0,7,1^(12b+24)] (m=1, r=2, t=3), so k2 = 12B+25.
  - The record's CDP rule then gives R2 with 2R2+4 = arrow(12B+26) 2 4. This escalation is solid.
- **P2 (exhaustion #2)** on n = 12B+25 is a base-5 Collatz-type chain: each sub-step takes v to about 3v/5, adds 3 to t and leaves a token.
  - Here n ≡ 36167 mod 5^9, so the chain stops after 5 sub-steps by residue.
  - It leaves tokens y1..y4, then the parked list 1^(12R2-10), then 0 2 z2, then a digit X = k3+7 behind k3 = (243n-32331)/3125 zeros, at t=18.
  - Checked literally on 5 values of n with R2 in {100, 346}; it needs R2 >= ~5.
- **J3** clears that digit, giving R3 << R2 (depth about 0.93B). The earlier grow worlds had R3 > R2, so they are NOT faithful past J3. The earlier "f_w^2(12B) to f_w^3" estimate and the "robust halt" claim are WITHDRAWN.
- **Exhaustion #3** is the same chain on k3, decided by n mod 5^(K+5). Still open:
  - (a) whether the real chain stops by residue, and in which terminal;
  - (b) whether J4 clears the parked 1^(12R2-c), which is the second escalation;
  - (c) whether H1 is reached.
  - The literal residue-faithful runs (pkf3 at K=7 and K=8) cost about n^2.
  - The agent is decoding the sub-step rule (affine maps by v mod 25; data in runs/etab_*.txt) so it can iterate the real 5-adic digits symbolically.
- **Bound.**
  - If C04 halts after J3 with no second escalation, σ ~ f_w(12B), which is BELOW fw2 (f_w(f_w 465009)).
  - It beats fw2 only if J4 clears 1^(12R2-c) and the machine then halts. That would give σ > f_w(f_w(12B)) > fw2.

## C04 update (2026-10-17 evening): probably Collatz-hard

- **The exhaustion chain is a base-5 Collatz map** on the D0 run length L, checked literally on 400 n (top level) and 40 n (post-J3), 0 mismatches. L0 = 3n-2 at top level and 3n-5 after J3. The map is:
  - L ≡ 1 (mod 5): L -> (3L+32)/5
  - L ≡ 2: L -> (3L-46)/5
  - L ≡ 3: L -> (3L-64)/5
  - L ≡ 4: L -> (3L-52)/5
  - L ≡ 0: stop, leaving a digit X = z+8 behind z = (L-30)/5 zeros.
  Each sub-step adds 3 to t. The real exhaustion #2 path is 108499 -> 65089 -> 39043 -> 23413 -> 14035.
- **Accumulators** enter only through a parked token 6R+9 and a parked list 1^(12R-c). The token to the left of the near region drops by 3 per exhaustion, so it is a counter.
- **Order-faithful world** (pkf --rk F --rc C, R = C + F*k): exhaustion #3 ends by residue (z=39), and exhaustion #4 ends by size and ACTIVATES the parked list (k = 12R2-39). So the second escalation, f_w(f_w(12B)), does happen there.
- **Why the halt can't be settled:**
  - Each level's cascade has about log(size) exhaustions, and their size-endgames depend on the LEADING digits of B-derived numbers, not on residues.
  - The B-scale counters run out mid-cascade, so the real run is a nested counter/cascade process.
  - Whether H1 is reached cannot be read off residues. C04 looks cryptid-like, and a proof is not realistic.
- **Closed:** C04 is not a usable record without a breakthrough. Approach #1 is closed with no G candidate.

## Final (bb9-parked2, 2026-10-17 night)

- chainsym.py runs the cascade on the real residues (B mod 5^200):
  - Exhaustion #3 stops by residue after 8 sub-steps, so J4 clears the near list, not the parked list.
  - Chains #4-#46 also stop by residue. The cascade runs about log(B) levels before its size endgame, and only that endgame can trigger the second escalation.
  - In the order-faithful world that endgame activated the parked list in 78 of 200 samples, with 0 halts.
- Unchecked assumption: L0 = 3(z+1)-5 for chains #4 and later (validated only for #3).
- The halt after that depends on leading digits and counter behaviour: Collatz-hard, undecided.
- Outcome classes:
  - halts after the level-2 escalation: σ > f_w(f_w(12B)) > fw2;
  - halts earlier (never seen): σ ~ f_w(12B) < fw2;
  - never halts: an f_(w+1)-shape looper.
- Full notes are in c04_notes.txt. Approach #1 is closed. C04 was handed to agent c04-fable (bb9_c04_deep/).
