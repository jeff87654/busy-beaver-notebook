import os, sys, collections

REB7_FAM = r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\final_all_families.tsv"
FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, FW1_DIR)
from bcfg import BASES

# Map each 7-state machine in BASES to its tag
base_to_tag = {}
for tag, (m7, _, B0, fam) in BASES.items():
    base_to_tag[m7] = (tag, fam, B0)

fams = {}
with open(REB7_FAM, "r") as f:
    hdr = f.readline().rstrip("\n").split("\t")
    for l in f:
        if not l.strip():
            continue
        p = l.rstrip("\n").split("\t")
        fid, rep, n, verdicts, stages, members, rules, emap = p
        mem_list = members.split(",")
        fams[fid] = {
            "fid": fid,
            "rep": rep,
            "n": int(n),
            "verdicts": verdicts,
            "stages": stages,
            "members": mem_list,
            "rules": rules,
            "emap": emap,
        }

print(f"Loaded {len(fams)} families from final_all_families.tsv")

# 1. Where do the 18 bases in bcfg.py appear in final_all_families.tsv?
print("\n=== 1. Location of the 18 bb8_fw1_redirect bases (a..u) in reb7/final_all_families.tsv ===")
for tag, (m7, _, B0, fam) in sorted(BASES.items()):
    found = []
    for fid, d in fams.items():
        if m7 in d["members"] or m7 == d["rep"]:
            found.append((fid, d["n"], d["rules"], d["emap"]))
    print(f"  [{tag}] ({fam}, B0={B0}) {m7} -> {found}")

# 2. Inspect F5, F44, F51, F70, F86, F89, F279 and all NEVER-HALTS families with halting or multi-class exhaustion or large rebuild
target_fids = ["F1", "F2", "F5", "F13", "F14", "F15", "F18", "F19", "F20", "F44", "F51", "F70", "F86", "F89", "F279"]
print("\n=== 2. Target reb7 families ===")
for fid in target_fids:
    if fid in fams:
        d = fams[fid]
        print(f"  {fid:5s} (n={d['n']:3d}, stages={d['stages']}) rep={d['rep']}")
        print(f"        rules: {d['rules']}")
        print(f"        emap : {d['emap']}")

# 3. Also list all S1 NEVER-HALTS families that have mod > 1 or coefficient >= 3 in rules/emap
print("\n=== 3. All S1 NEVER-HALTS families in final_all_families.tsv with mod >= 2 or slope >= 3 ===")
for fid, d in fams.items():
    if "NEVER-HALTS" in d["verdicts"] and ("mod 2" in d["emap"] or "mod 3" in d["emap"] or "mod 4" in d["emap"] or "3b" in d["rules"] or "4b" in d["rules"] or "5b" in d["rules"] or "3t" in d["emap"] or "4t" in d["emap"] or "6t" in d["emap"]):
        print(f"  {fid:5s} (n={d['n']:3d}) rep={d['rep']} | rules={d['rules']} | emap={d['emap']}")
