import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES

OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53'
CLS53 = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\cls53.txt'

entries = []
with open(CLS53, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('== '):
            parts = line.split()
            entries.append((parts[1], parts[2], ' '.join(parts[3:])))

assert len(entries) == 53

# 1. Write partA_summary.tsv
partA_tsv = os.path.join(OUT_DIR, 'partA_summary.tsv')
with open(partA_tsv, 'w', encoding='utf-8') as f:
    f.write("machine\tdlscan_template\ttrue_template\tverdict\tgrowth_class\tasymptotic_span\tasymptotic_digits\tcoq_proof\tunused_slots\tneighbor_max_halt\n")
    f.write(
        "1RB0LE_0RC1LF_1LD0RD_0LA---_1LA1RG_1RB1RF_0RH0LG_1RE1LD\t"
        "L,A,P=-,u=10,s=0,d=3d+2,b=1b+0,S=010101\t"
        "[E0] 010100101001 d_{c1}...d_{ck} (00101)^m (d0=0101001, d1=01001, d2=001)\t"
        "NEVER-HALTS(COUNTER/POLY+COQ_NGCPS)\t"
        "POLYNOMIAL_COUNTER(O(sqrt(t)))\t"
        "5*m + O(log m) = Theta(sqrt(t)) (~1.5e5 cells / ~3e4 blocks at 1.3e10 steps)\t"
        "k(t) = Theta(log_3(t)) ternary digits\t"
        "bb8_list/proofs/BB8_ng_1RB0LE0RC1LF1LD0RD0LAxxx1LA1RG1RB1RF0RH0LG1RE1LD.v (NGramCPS 14/14, 4182370 configs)\t"
        "D1=--- (all 15 other transitions used by step 35)\t"
        "348 steps (15 ones, G1->0RB) among all 465 1-transition neighbors\n"
    )

# 2. Classify all 53 machines in noinv53_verdicts.tsv
def classify_idx(idx, tag, tm, eb):
    fam = BASES[tag][3]
    if idx in (0, 16):
        return (
            "S1_EXP3",
            "NEVER-HALTS(EXP_3^r)",
            "inf",
            "EXP(3^r)",
            "K(X,2,2; 1; b) -> K(X; 2; b+2)",
            "No borrows used on [1, 2^m]; consumes 2s directly",
            "E(2m+1): HALT | E(2m): K([1, 2^(m+2)]; 1; 0)",
            "Closed-form E-chain: A_{r+1} = 3*A_r + 18 (always even, never halts)"
        )
    if idx in (1, 2):
        return (
            "S2_POLY",
            "NEVER-HALTS(QUADRATIC)",
            "inf",
            "POLY(t^2)",
            "K(X,2; 2; b) -> K(X; 2; b+1)",
            "Reduces [1, 2^(r-1)] in O(r) steps to E(3r+1)",
            "E(3r): HALT | E(3r-2): K([1, 2^(r-1)]; 2; 0)",
            "Closed-form E-chain: A_r = 3r - 2 == 1 (mod 3) forever (halts only for 0 mod 3)"
        )
    if idx in (15, 50, 51, 52):
        return (
            "S3_EXP4",
            "NEVER-HALTS(EXP_4^r)",
            "inf",
            "EXP(4^r)",
            "K(X,2,2; 2; b) -> K(X; 2; b+8)",
            "No borrows used on [4, 2^m]; consumes pairs of 2s directly",
            "E(1): HALT | E(2m): K([4, 2^(4m+7)]; 2; B0)",
            "Closed-form E-chain: L_{r+1} = 4*L_r + 16 (L_1=16, L_2=80, L_3=336, ...) with A=4 even at every E"
        )
    if idx == 22:
        return (
            "S4_TOWER3",
            "NEVER-HALTS(TETRATIONAL_3^^r)",
            "inf",
            "TETRATIONAL(f_4)",
            "K(X,2; a) -> K(X,0; 3a+6)",
            "B1: K(X,2,0; a) -> K(X,0; 3a+4) (shrinks list by 1 per step)",
            "E(2m): HALT | E(2m+1): K([2, 3, 2^(3m+1)]; 2; 0)",
            "B1 shrinks [2,3,2^m] in m steps multiplying a by 3 (a -> 3a+4, preserving odd a); every E(A_r) has A_r odd"
        )
    if idx == 43:
        return (
            "ACK_RESID",
            "NEVER-HALTS(FOMEGA1_RESIDUE)",
            "inf",
            "FOMEGA1",
            "D: b->b+3 | R2: K(X,d+1; 0; b) -> K(X,d; b+1; 3)",
            "Bk: K(X,d+1,0^k; 0; b) -> K(X,d,b-2k,3,2^(k-2); 3; 2) (B1:[b-2],a=4,b=2)",
            "E(b odd): HALT | E(2t): K([3, 2^(t-1)]; 3; 2)",
            "reb7.py 2-adic/mod-80640 & mod-483840 residue engine: 1-branch loop in class b == 0 (mod 2) forever"
        )
    if idx in (4, 11, 23, 25):
        return (
            "A1_INV_ODD_A",
            "NEVER-HALTS(FOMEGA1_INV_a_odd)",
            "inf",
            "FOMEGA1",
            "K(X,d+1; a) -> K(X,d; 3a+4)",
            "Bk (k mod 3 = 1,2,0): L_k = [3a+3-2k, 3,2,5,2,...] with a_k in {1, 3, 15} (ALL ODD)",
            "E(2m): HALT | E(2m+1): K([3, (2,5)^(m-1), 2, 4]; 15; B0)",
            "Exact invariant a == 1 (mod 2): every borrow B_k sets a_k in {1,3,15} odd, and D (a -> 3a+4) preserves odd a"
        )
    if idx in (6, 7, 8, 13, 14, 24, 27, 28):
        return (
            "A2_INV_ODD_A",
            "NEVER-HALTS(FOMEGA1_INV_a_odd)",
            "inf",
            "FOMEGA1",
            "K(X,d+1; a) -> K(X,d; 3a+4)",
            "Bk: a_1=5, and for k>=2 (k mod 3 = 1,2,0) a_k in {7, 3, 15} (ALL ODD)",
            "E(2m): HALT | E(2m+1): K([3, (2,5)^(m-1), 2, 4]; 15; B0)",
            "Exact invariant a == 1 (mod 2): every borrow B_k sets a_k in {3,5,7,15} odd, and D (a -> 3a+4) preserves odd a"
        )
    if idx in (9, 29):
        return (
            "E_INV_ODD_A",
            "NEVER-HALTS(FOMEGA1_INV_a_odd)",
            "inf",
            "FOMEGA1",
            "K(X,d+1; a) -> K(X,d; 3a+4)",
            "B1: K(X,d+1,0; a) -> K(X,d; 3a+4) | Bk (k>=2): L_k=[3a+2-2k, 5^(floor((k-2)/2))], a_k in {3, 5} (ODD)",
            "E(2m): HALT | E(2m+1): K([3, 5^m_E]; a_0 in {3,5}; 0)",
            "Exact invariant a == 1 (mod 2): B_k (k>=2) sets a_k in {3,5} odd, and both B_1 and D map a -> 3a+4 preserving odd a"
        )
    if idx in (10, 30):
        return (
            "F_INV_ODD_A",
            "NEVER-HALTS(FOMEGA1_INV_a_odd)",
            "inf",
            "FOMEGA1",
            "K(X,d+1; a) -> K(X,d; 3a+4)",
            "Bk (k mod 3 = 1,2,0): L_k=[3a+2-2k, (4,3)^*, ...], a_k in {9, 5, 21} (ALL ODD)",
            "E(2m): HALT | E(2m+1): K([2, (4,3)^(m-1), 4, 2]; 21; 0)",
            "Exact invariant a == 1 (mod 2): every borrow B_k sets a_k in {5,9,21} odd, and D (a -> 3a+4) preserves odd a"
        )
    if idx in (38, 48):
        return (
            "H_INV_ODD_A",
            "NEVER-HALTS(FOMEGA1_INV_a_odd)",
            "inf",
            "FOMEGA1",
            "K(X,d+1; a) -> K(X,d; 5a+6)",
            "B1: a_1=3 | B2: a_2=23 | Bk (k>=3): a_k in {5, 33} (ALL ODD)",
            "E(2m): HALT | E(2m+1): K([1, 3, 5^*...]; a_0 in {5,33}; 3)",
            "Exact invariant a == 1 (mod 2): every borrow B_k sets a_k in {3,5,23,33} odd, and D (a -> 5a+6) preserves odd a"
        )
    if idx in (39, 49):
        return (
            "I_INV_ODD_A",
            "NEVER-HALTS(FOMEGA1_INV_a_odd)",
            "inf",
            "FOMEGA1",
            "K(X,d+1; a) -> K(X,d; 5a+6)",
            "Bk (k>=1): L_k=[5a+6-2k, (1,3)^*...], a_k = 1 (k odd) or 3 (k even) (ALL ODD)",
            "E(2m): HALT | E(2m+1): K([1, 1, (3,1)^*...]; a_0 in {1,3}; 3)",
            "Exact invariant a == 1 (mod 2): every borrow B_k sets a_k in {1,3} odd, and D (a -> 5a+6) preserves odd a"
        )
    if idx == 3:
        return (
            "C_HALT_E3",
            "HALTS(ROUND_3_E3_FOMEGA)",
            "3",
            "FOMEGA(HALT@E3)",
            "K(X,d+1; a) -> K(X,d; 3a+4)",
            "B1: L_1=[3a], a_1=15 (odd) | B2: L_2=[3a-1], a_2=6 (even) (shrinks list by 1)",
            "E(2m): HALT | E(1)->K([1];7) | E(25)->K([1, 6, 5^17]; 6; 0)",
            "E1(1)->[1]->E2(25)->[1,6,5^17] (len 19, d1=1); B2 shrinks list 19->...->3 ([1,0,0]) where B2 gives K([3a-1]; 6) (even a), D preserves even a to E3 -> HALT"
        )
    if idx in (5, 12, 26):
        return (
            "D_HALT_E3",
            "HALTS(ROUND_3_E3_FOMEGA)",
            "3",
            "FOMEGA(HALT@E3)",
            "K(X,d+1; a) -> K(X,d; 3a+4)",
            "B1: L_1=[3a], a_1=14 (even) | B2: L_2=[3a-2], a_2=16 (even) | Bk (k>=3): |L_k|>=2, a_k in {23,25}",
            "E(2m): HALT | E(1)->K([1];23) | E(73)->K([2, 5^53, 4]; 23; 0)",
            "E1(1)->[1]->E2(73)->[2,5^53,4] (len 55>=2); only B1 and B2 can reduce list to len 1, setting a in {14,16} even, and D preserves even a to E3 -> HALT"
        )
    if idx in (36, 37, 46, 47):
        return (
            "G_HALT_E2",
            "HALTS(ROUND_2_E2_FOMEGA)",
            "2",
            "FOMEGA(HALT@E2)",
            "K(X,d+1; a) -> K(X,d; 5a+6)",
            "B1: L_1=[5a+2], a_1=25 (odd) | B2: L_2=[5a], a_2=8 (even) (shrinks list by 1)",
            "E(2m): HALT | E(21)->K([1, 1, 6, 8^16]; 10; 5)",
            "E1(21)->[1,1,6,8^16] (len 19, d1=1); only B1/B2 fire, shrinking list to [1,0,0] where B2 gives K([5a']; 8) (even a), D preserves even a to E2 -> HALT"
        )
    if idx in (17, 18, 19, 20, 21, 31, 32, 33, 34, 35, 40, 41, 42, 44, 45):
        return (
            "B_HALT_E2",
            "HALTS(ROUND_2_E2_FOMEGA)",
            "2",
            "FOMEGA(HALT@E2)",
            "D: (a+2,b)->(a,b+4) | R2: (U,r) -> (2U+8-r-((U+1)%2), (U+1)%2) where U=2a+b-r, r=a%2",
            "B1: L_1=[U], (U',r')=(9-r,0) | Bk (k>=2): L_k=[U+2-2k, 3, 2^(k-2)], (U',r')=(6-r,1)",
            "E(a,b) rebuilds iff U+r == 1 (mod 3) at [1,0]; halts otherwise",
            "E1(45)->[3,2^44] (len 45); B1 initializes U_0+r_0 in {0,2} (mod 3) and Phi_0 maps x -> -x+2 (mod 3) keeping U+r in {0,2} (mod 3), so E2 has A2 == 9358 (mod 49152) even -> HALT"
        )
    raise ValueError(f"Unclassified idx {idx}")

verdicts_tsv = os.path.join(OUT_DIR, 'noinv53_verdicts.tsv')
counts = {}
with open(verdicts_tsv, 'w', encoding='utf-8') as f:
    f.write("idx\ttag\tfamily\tmachine\tblank_E_trace\tgroup\tverdict\trounds_before_halt\tgrowth_class\texact_D_rule\texact_Bk_rule\texact_E_rule\tproof_mechanism\n")
    for idx, (tag, tm, eb) in enumerate(entries):
        fam = BASES[tag][3]
        grp, verd, rnds, gcls, drule, bkrule, erule, proof = classify_idx(idx, tag, tm, eb)
        counts[verd] = counts.get(verd, 0) + 1
        f.write(f"{idx}\t{tag}\t{fam}\t{tm}\t{eb}\t{grp}\t{verd}\t{rnds}\t{gcls}\t{drule}\t{bkrule}\t{erule}\t{proof}\n")

print("Verdict summary across all 53 machines:")
for k, v in sorted(counts.items()):
    print(f"  {v:2d}  {k}")
