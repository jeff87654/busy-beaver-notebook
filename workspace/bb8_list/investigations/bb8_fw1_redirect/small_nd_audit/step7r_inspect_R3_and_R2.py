from step7q_exact_dp_399 import std_399, traced3, get_d_aff, bdet

print("=== Inspecting all 13 Round-3 Halters in std_399 ===")
for r, t in zip(std_399, traced3):
    if t[0] == "HALT" and t[1] == 3:
        m_D, c_D = get_d_aff(r)
        bd = bdet[r["m"]]
        e_s = [f"{a}:{r['E'][a][4]};{r['E'][a][2]}" if r["E"][a][0]=="K" else f"{a}:{r['E'][a][0]}" for a in [1,2,3,4,5,6,7,8,15,16]]
        print(f"[{r['tag']}] {r['m']} D={m_D}a+{c_D}")
        print(f"  Trace: {t[3]}")
        print(f"  Blank: st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} first='{bd['first_ks']}'")
        print(f"  E: {e_s}")
        for k in (1, 2, 3, 4):
            print(f"  B{k}: odd={r['fit_B'][k][1][:6]} | even={r['fit_B'][k][0][:6]}")
            if k <= 3:
                print(f"  LB{k}: odd={r['fit_LB'][k][1][:6]} | even={r['fit_LB'][k][0][:6]}")
