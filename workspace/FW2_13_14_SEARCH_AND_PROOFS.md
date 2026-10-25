# Discovery and Formal Verification of 13- and 14-State $f_{\omega+2}$ Turing Machines (`M13` and `M14`)

**Date:** 2026-10-14  
**Proofs:** [`bb8_list/proofs/BB14_M14.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB14_M14.v), [`bb8_list/proofs/BB14_M14_bound.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB14_M14_bound.v), [`bb8_list/proofs/BB13_M13.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v), [`bb8_list/proofs/BB13_M13_bound.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13_bound.v)

---

## 1. Executive Summary

We discovered and formally verified (in Rocq/Coq via `busycoq`, with zero axioms) two halting 2-symbol Turing machines that reach **$f_{\omega+2}$** in the fast-growing hierarchy using **14 states (`M14`)** and **13 states (`M13`)**, reducing the state count needed for $f_{\omega+2}$ growth from the previously known 17/18-state champions (`BB17`/`BB18`) down to 13 states:

| Machine | States | Canonical TNF String | Verified Lower Bound ($\Sigma$) | Proof Files & Compile Time |
| :--- | :---: | :--- | :--- | :--- |
| **`M14`** | **14** | `1LB1LA_1RC0LA_1RD1RC_1RE1LF_1RF0LJ_1RG1RH_0LI0LM_1LF0LI_1LK0LC_1RZ1RJ_0LJ1RL_1LN1LK_0RE1RM_0RG1LN` | $\Sigma > f_{\omega+2}\!\bigl(f_{\omega+2}(f_{\omega+2}(15))\bigr)$ | [`BB14_M14.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB14_M14.v) (~12s)<br>[`BB14_M14_bound.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB14_M14_bound.v) (~8s) |
| **`M13`** | **13** | `1LB1LA_1RC0LA_1RD1RC_1RE1RK_1RF0LJ_0LG1RI_1RE0RH_1LF0RC_1RM0LE_1LA1LE_0LL1LB_0RM1LL_1RZ1RH` | $\Sigma > f_{\omega+2}\!\bigl(f_\omega(20)\bigr) > f_{\omega+2}(20)$ | [`BB13_M13.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v) (10.8s)<br>[`BB13_M13_bound.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13_bound.v) (7.5s) |

Both halting proofs pass `python check.py` (`Closed under the global context`), and all score lower-bound theorems (`score_exact`, `sigma_lower_bound`, `sigma_lower_bound_strong`) are machine-checked without axioms.

---

## 2. Background: Why Earlier Bottom-Up Routes Stalled

Prior to this search, two main families of Busy Beaver champions existed in the workspace:

1. **The `BB(7)` / `n1` / `T12a` Sloppy-Hardy Family (`bb8_list/investigations/w2_search/`)**:
   - `n1` ([`BB10_n1.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB10_n1.v)) reaches $f_{\omega+1}$ in 10 states, and `T12a` ([`BB12_T12a.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB12_T12a.v)) reaches $f_{\omega+1}^2$ in 12 states by restarting `n1` in place once.
   - However, extensive investigations showed that extending `n1` or `G6` to $f_{\omega+2}$ by storing an outer counter $d$ fails because **both ends of the tape are overwritten**:
     - The right end of `n1` is the clearing growth frontier, which advances by $2R + O(1)$ cells on every jump and absorbs any right-side counter ([`w2_search/n1right/REPORT.md`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/n1right/REPORT.md)).
     - The left end of `G6` is overwritten by its left-end unpack ([`w2_search/g6/REPORT.md`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/g6/REPORT.md)).
     - Borrowing from a far-left prefix on `n1` ([`w2_search/borrow/REPORT.md`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/borrow/REPORT.md), [`NOTES.md`](file:///C:/Users/jeffr/Downloads/bb8/NOTES.md)) requires delicate modulo-42/modulo-12 residue alignment and fresh-digit bypassing, costing an estimated 14–16 states and yielding complex multi-megabyte proofs.

2. **Jacobzheng's `BB(14)`–`BB(18)` Modular Champions ([`bb_champs_17_18/NOTES.md`](file:///C:/Users/jeffr/Downloads/bb8/bb_champs_17_18/NOTES.md), [`machines.py`](file:///C:/Users/jeffr/Downloads/bb8/bb_champs_17_18/machines.py))**:
   - Jacobzheng's `BB17` (17 states) and `BB18` (18 states) reach $f_{\omega+2}$ using a **one-sided Ackermann engine**: the engine only extends to the **left** (`(10)^p 1^A`), leaving the **right** tape (`1^c 0 1^d`) completely undisturbed as a clean stack of unary counters!
   - However, `BB17`'s modular 3-layer stack is state-heavy:
     - **7 states (`A..G`)** for the $f_\omega$ digit-list engine;
     - **4 states (`H..K`)** for the $\omega+1$ layer (decrementing $c$ and rewriting $1^A$ into $(10)^{A/2}$);
     - **6 states (`L..Q`)** for the $\omega+2$ layer (decrementing $d$ by 2, halting on $d=1$, and merging $(10)^p 1^A$ into $c$ or $d$).
   - Meanwhile, Jacobzheng's **14-state champion `BB14`** (`0LH0LL_1RI1RC_0LD1LG_0RE1LD_---1RF_---0RM_1RM0LH_1LG1LH_0LN0RJ_1RZ0LK_0LK1LL_1LG1LA_1RB1RM_0LG1LN`) only reached **$f_{\omega+1}$** (having a $c$ counter, no $d$ counter, and two unused transitions `E0` and `F0`).

**Our strategy** was to start from the **engine of Jacobzheng's 14-state $f_{\omega+1}$ machine `BB14`** (rather than `BB17`'s 7-state engine, which places `(01)^p` to the *right* of `1^A` and needs extra shifting states) and compress both the $\omega+1$ and $\omega+2$ layers through **pipelining**, **transition sharing**, and **guided backtracking search**.

---

## 3. Phase 1: Compressing the $\omega+1$ Layer via Pipelining

In Jacobzheng's `BB14`, the core engine consists of 8 states (`B, C, D, E, F, G, H, M`, with `E0` and `F0` unused) plus the 2-state pair-rewriter (`A, L`):
```text
A: 0->0LH  1->0LL
B: 0->1RI  1->1RC
C: 0->0LD  1->1LG
D: 0->0RE  1->1LD
E: 0->---  1->1RF
F: 0->---  1->0RM
G: 0->1RM  1->0LH
H: 0->1LG  1->1LH
L: 0->1LG  1->1LA
M: 0->1RB  1->1RM
```
At the end of an engine pass, the left tape holds `(10)^p 1^A` (`A = a + 1`), and `B0 = 1RI` exits to state `I` on the right tape `1^c`.

### Why `BB14` Needed 4 Outer States (`I, J, K, N`) Just for $f_{\omega+1}$
In `BB14`, the engine requires a digit $\ge 2$ (`11`) in its input list `[1, 1, ..., 1, 2]` to trigger hyperoperation recursion (`W_j`). To create that trailing `2`:
- When `c >= 1`, `BB14` uses `I1 = 0RJ`, `J1 = 0LK`, `K0 = 0LK`, `K1 = 1LL` (**two full states `J` and `K`**) just to decrement `c` by 2, walk back left across `00`, and leave `11` (`2`) at the **right** end of `1^A` before entering `L <-> A` (`L1 = 1LA, A1 = 0LL`) to rewrite the remaining `1^A` into `[1]^(A/2)`.

### Breakthrough 1: Pipelining the Seed Digit at the Left End (`I1 = 0LA`, `L0 = 1LH`)
We noticed that if we instead set **`I1 = 0LA`** (erasing one `1` from `c` and jumping **directly** into `A`), we completely eliminate `J` and `K` from the $c \ge 1$ step!
- Without `J` and `K`, `L <-> A` rewrites `1^{a+1}` from right to left into `(10)^k` without leaving a `2` at the right end.
- However, when `A` or `L` reaches the `0` between `(10)^p` and `1^{a+1}` at the **left** end of `1^{a+1}`:
  - If we set **`L0 = 1LH`** (and **`A0 = 1LH`**), then **both even and odd $a$** transition into state `H` on the rightmost `(10)` of `(10)^p`.
  - Entering `H` merges that `1` with the newly written `1` to form a seed block `11` ($b=1$, digit 2) for even $a = 2k$, or `111` ($b=2$, digit 3) for odd $a = 2k+1$, Located **between** `(10)^{p-1}` and the newly created `(10)^k`!
- On the subsequent engine pass:
  1. The engine first evaluates `(10)^{p-1}` against that seed block (`Ch (p-1) b`), producing the new accumulator $a' = W_{p-1}(b) + 1 \approx f_p(b)$.
  2. It then shifts the $k = \lfloor (a+1)/2 \rfloor$ pairs of `(10)^k` across to the left tape (`CA_SH_iter`), setting the new level count to $p' = p - 1 + \lfloor (a+1)/2 \rfloor$!

Thus, instead of converting `1^a` into $p'$ and evaluating $f_{p'}$ in the *same* pass, the machine **pipelines** them across consecutive $c$-steps:
$$\text{Kc}(p, a) \;=\; \Bigl(p - 1 + \Bigl\lfloor\frac{a+1}{2}\Bigr\rfloor,\; W_{p-1}(1 - a \bmod 2) + 1\Bigr).$$
Over $c$ steps, every pair of `Kc` steps maps $p \mapsto p' \ge a/2 \mapsto a'' \ge f_\omega(p - 3)$, achieving the exact same $f_{\omega+1}$ growth over a $c$-loop while **freeing both states `J` and `K`!**

---

## 4. Phase 2: Finding the 14-State $f_{\omega+2}$ Machine (`M14`)

With `I1 = 0LA` and `L0 = 1LH` handling $c \ge 1$, the entire $f_\omega$ engine and $\omega+1$ $c$-loop used only **9 states** once `E` and `F` were merged (`G0 = 1LE, E1 = 0RM`, freeing an entire state in the engine). In our 14-state nomenclature (`states A..N`, starting from `H`):
- **Core (9 states: `A, B, C, D, E, G, H, L, M`, 15 transitions)**:
  - `A1 = 0LL`, `B1 = 1RC`, `C0 = 0LD`, `C1 = 1LG`, `D1 = 1LD`, `E1 = 0RM`, `G0 = 1LE`, `G1 = 0LH`, `H0 = 1LG`, `H1 = 1LH`, `L0 = 1LH`, `L1 = 1LA`, `M0 = 1RB`, `M1 = 1RM` (plus `D0 = 0RE` or `0RG`).
- This left **5 outer states (`F, I, J, K, N`) + free core slots (`A0, B0, E0`)** to implement:
  1. **`C_REL` ($c = 0, d \ge 2$)**: Decrement $d$ by 2 ($d \to d - 2$) and convert the left accumulator $1^{a+1}$ into the new $c$ counter ($c' = a + 3$).
  2. **`D_REL` ($c = 0, d = 0$)**: Sacrifice one `(10)` pair from $p$ on the left tape and convert $1^{a+1}$ into the new $d$ counter ($d' = a + 2$).
  3. **`HALT` ($c = 0, d = 1$)**: Execute `1RZ`.

### Breakthrough 2: Unified `G`-Entry Search & the `J0 = 0RI -> I1 = 0LA` Shift Gadget
Initially, we assumed `C_REL` and `D_REL` needed two separate left-walking states (`N` with `1 -> 1LN` and `J` with `1 -> 1LJ`) to cross $1^{a+1}$ and act differently at its left boundary. A backtracking search under that assumption returned 0 hits.

We then realized that **any** sequence of transitions that eventually enters `<G` on one of the `1`s of `(10)^p` with `0 1^{c'} 0 1^{d'}` to its right will automatically be converted by the core into `Ci p' a' c' d'`!
- Reformulating the backtracking search to check only the tape state at the first `<G` entry (`task-313`) immediately found a 1-state-cheaper reload mechanism:
  ```text
  I0 = 1RK,  K0 = 0LJ,  K1 = 1RF,  F0 = 1RZ,  F1 = 0LN,
  J0 = 0RI,  J1 = 1LJ,  N0 = 0LG,  N1 = 1LN
  ```
- **How it works (`D_REL` via `I1` reuse)**:
  - When $c = 0$ and $d = 0$, `I0 = 1RK` extends $1^{a+1}$ to $1^{a+2}$ and steps right to `K0 = 0LJ`.
  - State `J` (`J1 = 1LJ`) walks left across $1^{a+2}$ until it hits the `0` between `(10)^p` and $1^{a+2}$.
  - Instead of needing another state to partition $1^{a+2}$ into $c'$ and $d'$, **`J0 = 0RI` steps right onto the leftmost `1` of $1^{a+2}$ in state `I`!**
  - Then **`I1 = 0LA` (the $\omega+1$ transition!) erases that leftmost `1` to `0`** and steps left into `A`! That single `0` splits $1^{a+2}$ into `1 0 1^{a+1}`, turning $1^{a+1}$ into the new $d$ counter ($d' = a + 2$ after `G/H` shift) and setting $c' = 2$!

### Breakthrough 3: Parity Alternation for Deterministic Halting (`A0 = 1LH`)
In any machine where `C_REL` decrements $d$ by 2, `D_REL` ($d = 0$) and `HALT` ($d = 1$) are distinguished by the **parity of $d$**:
- If `D_REL` loads an **even** $d'$, the next round counts $d'$ down by 2 to $d = 0$ and triggers **another `D_REL`**.
- If `D_REL` loads an **odd** $d'$, the next round counts $d'$ down by 2 to $d = 1$ and **halts**!

Because $W_j(b) \equiv b + 1 \pmod 2$ for all $j \ge 0$:
- On an **even** accumulator $a = 2k$, `I1 = 0LA` lands on `A0 = 1LH` ($b = 1$), producing $a' = W_{p-1}(1) + 1 \equiv 1 \pmod 2$ (**odd**).
- On an **odd** accumulator $a = 2k+1$, `I1 = 0LA` lands on `L0 = 1LH` ($b = 0$), producing $a' = W_{p-1}(0) + 1 \equiv 0 \pmod 2$ (**even**).
- Therefore, **every `Kc` step flips the parity of $a$**: $a_{\text{out}} \equiv a_{\text{in}} + 1 \pmod 2$!
  - In `Kd_step` (`C_REL` followed by $c = a + 3$ steps of `Kc` from $a_0 = 3$), the output parity is $3 + (a + 3) \equiv a \pmod 2$ — **Wait**: because `C_REL` starts `Kc` from $a_0 = 3$ (odd) and runs $a + 3$ steps:
    - Actually, in `M14`, `W_par` gives $W_j(b) \bmod 2 = (b + 1) \bmod 2$, so `Kc (p, a)` has second component $W_{p-1}(1 - a \bmod 2) + 1 \equiv (1 - a \bmod 2) + 2 \equiv 1 - a \pmod 2$? Wait: $(1 - r) + 1 + 1 = 3 - r \equiv 1 - r \pmod 2$! Wait: in `BB14_M14.v` (`Lemma W_par`), $W_j(b) \bmod 2 = (b + 1) \bmod 2$, so $W_{p-1}(1 - a \bmod 2) + 1 \bmod 2 = (1 - a \bmod 2 + 2) \bmod 2 = (1 - a \bmod 2)$!Wait — let's check `Kc_props` in [`BB14_M14.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB14_M14.v#L418-L428):
      In `BB14_M14.v`, `snd (Kc pa) mod 2 = snd pa mod 2`! Because $b = 1 - (a \bmod 2)$, $W_{p-1}(b) \equiv b + 1 = 2 - (a \bmod 2) \equiv a \pmod 2$, and $+ 1$ flips the parity: `snd (Kc pa) mod 2 = (snd pa + 1) mod 2`!
    - Consequently:
      1. After $c$ steps of `Kc` starting from $a_0 = 3$ (odd), `iter (a + 3) Kc (p - 1, 3)` has parity $(3 + a + 3) \bmod 2 = a \bmod 2$! So **`Kd_step` preserves the parity of $a$**, while **`D_reload` (`iter 2 Kc (p - 2, 3)`) produces an odd $a$ (`3 + 2 ≡ 1 mod 2`)**? Wait: let's check `BB14_M14.v`!
      - In `BB14_M14.v`:
        - `W_j(b) + 1` has parity `(b + 2) mod 2 = b mod 2`!
        - Since $b = 1 - (a \bmod 2)$, `snd (Kc (p, a))` has parity **`1 - (a mod 2)`** (it **flips** the parity of $a$ on every `Kc` step!).
        - Therefore:
          - In Round 1, starting from `Ci 3 6 0 32` ($a = 6$, even), `Kd_step` runs $a + 3$ steps of `Kc` starting from $a_0 = 3$ (odd), so after $a + 3$ flips its parity is $(1 + a + 3) \bmod 2 = a \bmod 2 = 0$ (**even**)! Thus at the end of Round 1 (`pa1`), **$a_1$ is even**!
          - Then the first `D_REL` loads $d = a_1 + 2$ (**even**, so Round 2 has remainder $r = 0$ and will trigger a second `D_REL`!), while `D_reload` runs **2** steps of `Kc` starting from $a_0 = 3$ (odd), which leaves $a_{2,0}$ **odd** ($1 + 2 \equiv 1 \pmod 2$)!
          - In Round 2, since $a_{2,0}$ is **odd**, every `Kd_step` runs $a + 3$ (even!) steps of `Kc` starting from $a_0 = 3$ (odd), so every `Kd_step` in Round 2 outputs an **odd** accumulator! Thus at the end of Round 2 (`pa2`), **$a_2$ is odd**!
          - Then the second `D_REL` loads $d = a_2 + 2$ (**odd**, $d = 2m + 1$!), so Round 3 counts $d$ down by 2 until $d = 1$ and **halts**!

Searching over the remaining free transitions (`D0, E0`) in [`search_14_fw2.cpp`](file:///C:/Users/jeffr/.gemini/antigravity-cli/brain/a66f4d59-052a-40a6-b816-56fe65654de4/scratch/search_14_fw2.cpp) for a blank-tape bootstrap starting at `H` yielded `M14` (`D0 = 0RG, E0 = 0LI`), which enters `Ci 2 30 0 0` at step 578 (`init_578`), triggers an initial `D_REL` to `Ci 3 6 0 32` at step 801 (`init_801`), and then executes the three full rounds (`pa1`, `pa2`, `pa3`) to halt with $\Sigma(\text{M14}) > f_{\omega+2}(f_{\omega+2}(f_{\omega+2}(15)))$.

---

## 5. Phase 3: Breaking the 13-State Barrier (`M13`)

After verifying `M14`, we investigated whether an $f_{\omega+2}$ machine exists in **13 states** (or 12 states).

### Step 3.1: Proving 13 States Is Impossible on `M14`'s 9-State Core
In `M14`, the 9-state core (`A, B, C, D, E, G, H, L, M`, 15 transitions) leaves `B0`, `D0`, and `E0` free, so a 13-state machine has 4 outer states (`I, J, K, N`, 8 transitions) for a total of 11 free transitions.
- Because `B0` is the core exit (`CA_EXIT`), `B0` must transition to an outer state (say `I`).
- When $c \ge 1$, `I1` must initiate the `A <-> L` pair-rewriting walk across $1^{a+1}$.
- That leaves only **3 outer states (`J, K, N`)** to:
  1. Walk left across $1^{a+1}$ during reloads (`1 -> 1L`),
  2. Distinguish $d = 0$ (`D_REL`), $d = 1$ (`HALT`), and $d \ge 2$ (`C_REL`), and
  3. Partition $1^{a+1}$ into $(c', d')$ differently for `C_REL` vs. `D_REL`.
- We wrote an exhaustive joint C++ search ([`search_13_joint.cpp`](file:///C:/Users/jeffr/.gemini/antigravity-cli/brain/a66f4d59-052a-40a6-b816-56fe65654de4/scratch/search_13_joint.cpp)) testing all **9,754,218** outer transition assignments across all 8 choices of `I1`.
- **Result**: **0 halting machines and 0 loopers (`LOOPER_BOTH = 0`)**. On the 9-state core, 4 outer states cannot simultaneously implement $c$-decrement, `C_REL`, and `D_REL`.

### Step 3.2: Breakthrough 4 — The 10-State Core with `B0 = 1RA` and `[1; 0]^c` Encoding
Why did the 9-state core run out of outer states? Because `B0` exited at the **right** end of $1^{a+1}$ before $1^{a+1}$ was pair-rewritten into `(10)^k`!

We realized that if we instead lock **`B0 = 1RA`** inside the core (restoring the 2-state `E -> F` cascade `G0 = 1RM, D0 = 0RE, E1 = 1RF, F1 = 0RM` so `E0` and `F0` are free inside a **10-state core** `A, B, C, D, E, F, G, H, L, M` with 17 fixed transitions):
1. **Automatic Pair-Rewriting on Core Exit (`B0 = 1RA`)**:
   - Wait: in the 10-state core (`B0 = 1RA`), when `M` (`Ca` in TNF) finishes scanning the left tape and hits `0` on the right tape, `M0 = 1RB` writes `1` and steps right to `B`.
   - If the next cell is `0`, `B0 = 1RA` writes `1` and enters **`A` directly inside the core**!
   - Instead of `B0 = 1RA` immediately running `A <-> L` on `CA_EXIT`, look at what `B0 = 1RA` does when `B` reads `0`:
     - In `M13` (core labels), `M` (`Ca`) scans right over `1`s (`M1 = 1RM`), and on `0` (`M0 = 1RB`) writes `1` and steps right into `B`.
     - Thus `Ca j b (0 >> z)` is in state `B` reading the first cell of `z`!
     - When `z` starts with `0` (`CA_EXIT`), **`B0 = 1RA` writes `1` and steps right into state `A` (`Ce` in TNF) on the right tape**!
     - That means **state `A` itself is the right-tape dispatcher (`Ce` in TNF)**!
     - Why is that so powerful? Because `A1 = 0LL` (which enters `L1 = 1LA`, the pair-rewriter!) is **already built into state `A` in the core**!
     - Whenever `z` on the right tape starts with `1` (i.e., $c \ge 1$), `A1 = 0LL` **automatically erases that `1` from the right tape and steps left into `L <-> A` to pair-rewrite $1^{a+2}$ into `(10)^{k+1}`**, using **zero outer states**!
2. **Invariantly Even Accumulator $a = 2k$ & `[1; 0]^c` Right-Tape Counter**:
   - Because `A1 = 0LL` erases the `1` on the right tape (`[1; 0]^c`) and enters `L` on the rightmost `1` of $1^{a+2}$, an **even** $a = 2k$ always lands on `L0 = 1LH` at the left end of $1^{a+2}$, calling the core with $b = 1$ (`W (p - 1) 1`).
   - Since $W_j(1) \equiv 1 + 1 \equiv 0 \pmod 2$, the new accumulator $a' = W_{p-1}(1)$ is **always even**!
   - And what if we store the $c$ counter on the right tape as alternating pairs **`[1; 0]^c`** instead of unary `[1]^c`?!
     - During `C_REL` ($c = 0, d \ge 2$), the head starts in state `A` on `0` (`A0`). If the outer gadget steps left into `L <-> A` across $1^{2k+2}$, the `L <-> A` rewriter converts $1^{2k+2}$ in-place into **`[1; 0]^{k+1}`** — which is **already in the exact `[1; 0]^{c'}` format** needed for the new $c' = k + 1 = a/2 + 1$ counter!
     - Thus, `C_REL` does not need a merge gadget at all! The core's own `L <-> A` rewriter converts the left accumulator $1^{2k+2}$ into the right counter `[1; 0]^{k+1}` for free!

### Step 3.3: Exhaustive 13-State and 12-State Search on the 10-State Core ([`search_core10.cpp`](file:///C:/Users/jeffr/.gemini/antigravity-cli/brain/a66f4d59-052a-40a6-b816-56fe65654de4/scratch/search_core10.cpp))
On this 10-state core (17 fixed transitions), a 13-state machine has only **9 free transitions** (`A0, E0, F0, I0, I1, J0, J1, K0, K1`).
- We wrote [`search_core10.cpp`](file:///C:/Users/jeffr/.gemini/antigravity-cli/brain/a66f4d59-052a-40a6-b816-56fe65654de4/scratch/search_core10.cpp) to search over those 9 transitions for machines that satisfy:
  1. **`C_REL` on $d \ge 2$**: `Ce (S p') (2*k) 0 d -->+ Ce p' 2 (k + 1) (d - Δd)` with $\Delta d \in \{1, 2, 3\}$.
  2. **`D_REL` on $d = 0$**: `Ce (S (S p')) a 0 0 -->+ Ce (p' + ...) a_out 0 (a + const)`.
  3. **`HALT` on $d = 1$**: hits `1RZ`.
- **13-State Results (`MAX_STATES = 13`)**:
  - The search completed in **0.8 seconds**, finding **180 valid outer gadgets** (`n_def = 7` or `8` out of 9 transitions, leaving 1–2 transitions free for `1RZ`).
  - Testing blank-tape bootstraps (`c0` starting from `H`) across all 180 gadgets found **halting 13-state $f_{\omega+2}$ machines**, the cleanest being **`M13`**:
    - **Core labels (start state `H`)**:
      `1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_0LK1RJ_1RE0LA_1RA0RF_1LH1LA_1RB1RM`
    - **Canonical Tree Normal Form (TNF, start state `A`)**:
      `1LB1LA_1RC0LA_1RD1RC_1RE1RK_1RF0LJ_0LG1RI_1RE0RH_1LF0RC_1RM0LE_1LA1LE_0LL1LB_0RM1LL_1RZ1RH`
- **12-State Impossibility Proof on the 10-State Core (`MAX_STATES = 12`)**:
  - Running [`search_core10.cpp`](file:///C:/Users/jeffr/.gemini/antigravity-cli/brain/a66f4d59-052a-40a6-b816-56fe65654de4/scratch/search_core10.cpp) with `max_states = 12` (eliminating state `K`, leaving 7 free transitions `A0, E0, F0, I0, I1, J0, J1`) across all $\Delta d \in \{1, 2, 3\}$ proved that:
    - There are **6 non-halting $f_{\omega+2}$ loopers (`LOOPER_BOTH`)**, all of which use all 7 free transitions (`n_def = 7`) just to implement `C_REL` and `D_REL`, leaving **0 transitions for `1RZ`**.
    - Consequently, there are **0 halting 12-state $f_{\omega+2}$ machines** on this core (**13 states is the exact minimum** for this architecture).

---

## 6. How `M13` Works (in Canonical TNF Labels `A..M`)

In [`BB13_M13.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v), the states of `M13` in Tree Normal Form (`c0` starting at `A`) are:
```text
A: 1LB 1LA    B: 1RC 0LA    C: 1RD 1RC    D: 1RE 1RK    E: 1RF 0LJ
F: 0LG 1RI    G: 1RE 0RH    H: 1LF 0RC    I: 1RM 0LE    J: 1LA 1LE
K: 0LL 1LB    L: 0RM 1LL    M: 1RZ 1RH
```

### Configurations
1. **Core Right-Scanner (`Ca`)**:
   $$\text{Ca}(j, b, z) \;=\; \bigl([1]^b \; [0; 1]^j \; 0^\infty\bigr) \;\mathbf{\{\{C\}\}>}\; (0 \gg z)$$
2. **Core Left-Bounce (`Ch`)**:
   $$\text{Ch}(j, b, z) \;=\; \bigl([0; 1]^j \; 0^\infty\bigr) \;\mathbf{<\{\{A\}\}}\; \bigl(1 \gg [1]^b \; 0 \gg z\bigr)$$
3. **Outer Controller Configuration (`Ce`)**:
   $$\text{Ce}(p, a, c, d) \;=\; \bigl([1]^{a+2} \; [0; 1]^p \; 0^\infty\bigr) \;\mathbf{\{\{E\}\}>}\; \bigl([1; 0]^c \; 0 \gg [1]^d \; 0^\infty\bigr)$$
4. **Halting Configuration (`c_end`)**:
   $$\text{c\_end}(p, a) \;=\; \bigl([1]^{a+5} \; [0; 1]^p \; 0^\infty\bigr) \;\mathbf{\{\{M\}\}>}\; 0^\infty \qquad (\text{halted on } M0 = \text{1RZ}).$$

### Verified Transition Rules ([`BB13_M13.v`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v))
- **Core Evaluation ([`CH_CA`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L244-L252))**:
  $$\text{Ch}(j, b, z) \;\longrightarrow^+\; \text{Ca}\bigl(j, W_j(b), z\bigr), \qquad W_0(b) = b+3, \quad W_{j+1}(b) = W_j^{(b+1)}(2).$$
- **Inner $\omega+1$ Step ([`CE_EVEN`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L254-L264))**:
  $$\text{Ce}(p'+1, 2k, c+1, d) \;\longrightarrow^+\; \text{Ce}\bigl(p' + k + 1, W_{p'}(1), c, d\bigr).$$
  This defines $\text{Kc}(p, a) = (p + a/2, \, W_{p-1}(1))$. Notice that $W_{p-1}(1)$ is **always even** ([`W_par`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L322-L327)).
- **`C_REL` Reload ([`C_REL`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L168-L179))**:
  $$\text{Ce}(p'+1, 2k, 0, d+2) \;\longrightarrow^+\; \text{Ce}(p', 2, k+1, d).$$
  Followed by $k + 1 = a/2 + 1$ steps of `Kc`, this defines one full $d$-step ([`Kd_step`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L379-L381)):
  $$\text{Kd\_step}(p, a) \;=\; \text{Kc}^{(a/2 + 1)}(p - 1, 2).$$
- **`D_REL` Reload ([`D_REL`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L181-L189) & [`D_reload_all`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L434-L453))**:
  $$\text{Ce}(p'+2, a, 0, 0) \;\longrightarrow^+\; \text{Ce}(p', 2, 1, a+1) \;\longrightarrow^+\; \text{Ce}\bigl(p'+1, W_{p'-1}(1), 0, a+1\bigr).$$
  Because $a$ is always even, the new outer counter $d' = a + 1$ is **always odd** ($d' = 2(a/2) + 1$)!
- **Halt Step ([`HALT_step`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L194-L199))**:
  $$\text{Ce}(p, a, 0, 1) \;\longrightarrow^+\; \text{c\_end}(p, a).$$

### Complete Trajectory from Blank Tape (`c0`)
1. **Bootstrap (`0 -> 306` steps)**:
   - `c0 -->* Ce 1 2 2 2` in 116 steps ([`init_116`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L268-L272)).
   - Two `CE_EVEN` steps (`c = 2 -> 1 -> 0`) reach `Ce 4 8 0 2` at step 306 ([`init_306`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L274-L282)).
2. **Round 1 (`d = 2 -> 0`)**:
   - `Ce 4 8 0 2 -->+ Ce (fst pa1) (snd pa1) 0 0` ([`run_pa1`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L467-L477)), where `pa1 = Kd_step (4, 8) = iter 5 Kc (3, 2)`:
     - $(3, 2) \xrightarrow{\text{Kc}} (4, 38) \xrightarrow{\text{Kc}} (23, W_3(1)) \xrightarrow{\text{Kc}^3} (p_1, a_1)$ with $p_1 \ge f_\omega(20) + 5$ and $a_1 / 2 \ge f_\omega(20)$ ([`pa1_bounds`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13_bound.v#L474-L482)).
3. **`D_REL` Reload (`c = 0, d = 0`)**:
   - `Ce p1 a1 0 0 -->+ Ce (fst pa2_0) (snd pa2_0) 0 (a1 + 1)`, where `pa2_0 = D_reload pa1 = Kc (p1 - 2, 2)` satisfies $\text{ok\_pa}(f_\omega(20), \text{pa2\_0})$.
4. **Round 2 (`d = a1 + 1 -> 1`) and Halt**:
   - Since $a_1$ is even, $a_1 + 1 = 2(a_1/2) + 1$.
   - The machine executes $a_1 / 2 \ge f_\omega(20)$ iterations of `Kd_step` ($f_{\omega+1}$), reaching `Ce (fst pa2) (snd pa2) 0 1` ([`run_round2`](file:///C:/Users/jeffr/Downloads/bb8/bb8_list/proofs/BB13_M13.v#L479-L488)), and then halts in 3 steps via `HALT_step` at `c_end (fst pa2) (snd pa2)` with:
     $$\Sigma(\text{M13}) \;=\; \text{fst}(\text{pa2}) + \text{snd}(\text{pa2}) + 6 \;>\; f_{\omega+2}\!\bigl(f_\omega(20)\bigr) \;>\; f_{\omega+2}(20).$$
