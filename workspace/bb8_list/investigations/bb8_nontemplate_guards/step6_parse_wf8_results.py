import os, sys, glob, re

OUR_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_nontemplate_guards"
OUT_DIR = os.path.join(OUR_DIR, "scr_x33")

TARGETS = [
    ("X33",   "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE", 470, [33]),
    ("Z16",   "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE", 476, [33]),
    ("Y19",   "1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LA0LG_1LB1LG", 459, [43]),
    ("F70",   "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LG0LE_1RA---", 481, [4, 19]),
    ("F279",  "1RB0LA_0RC0RG_1RD---_0LE0LF_1LE0RF_1LF1RA_0RD0RG",  84, [33, 42]),
    ("F44a",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LG0LE_0RA---", 478, [4, 19]),
    ("F44b",  "1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LG0LE_1RE---", 474, [4, 19]),
]

print("=================================================================")
print("1. WF8 RESULTS ON REACHABLE ROUND-1 RESIDUES (c=33 FOR X33/Z16, c=43 FOR Y19)")
print("=================================================================")

for name, m, idx, true_cs in TARGETS:
    files = sorted(glob.glob(os.path.join(OUT_DIR, f"{idx:03d}_*.txt")))
    res_files = [f for f in files if not f.endswith("_snap.txt")]
    
    verdict_counts = {}
    j_pos_halts = []
    t_j_pos = []
    
    for rf in res_files:
        bname = os.path.basename(rf)
        # Check if _c<num>_ is in true_cs
        m_c = re.search(r"_c(\d+)_", bname)
        c_val = int(m_c.group(1)) if m_c else -1
        if c_val not in true_cs:
            continue
        for line in open(rf):
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            verd = parts[1]
            m_j = re.search(r"\bJ=(\d+)", line)
            m_esc = re.search(r"\besc=(\d+)", line)
            m_maxk = re.search(r"\bmaxk=(\d+)", line)
            J = int(m_j.group(1)) if m_j else 0
            esc = int(m_esc.group(1)) if m_esc else 0
            maxk = int(m_maxk.group(1)) if m_maxk else 0
            
            key = f"{verd}(J>0)" if J > 0 else f"{verd}(J=0)"
            verdict_counts[key] = verdict_counts.get(key, 0) + 1
            if verd == "HALT" and (J > 0 or esc > 0 or maxk > 0):
                j_pos_halts.append((bname, line.strip()))
            elif verd == "T" and J > 0:
                t_j_pos.append((bname, line.strip()))
                
    print(f"\n[{name}] (i={idx}, true_c={true_cs}):")
    print(f"  Verdict summary: {verdict_counts}")
    print(f"  HALT with J>0 / esc>0 / maxk>0: {len(j_pos_halts)}")
    for bf, ln in j_pos_halts[:10]:
        print(f"    [{bf}] {ln}")
    print(f"  T with J>0: {len(t_j_pos)}")
    for bf, ln in t_j_pos[:10]:
        print(f"    [{bf}] {ln}")
