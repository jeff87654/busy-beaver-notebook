import os, sys

REB7_FAM = r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\final_all_families.tsv"
FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
sys.path.insert(0, FW1_DIR)
from bcfg import BASES

base_set = {v[0]: k for k, v in BASES.items()}

with open(REB7_FAM, "r") as f:
    hdr = f.readline()
    for l in f:
        if not l.strip():
            continue
        fid, rep, n, verdicts, stages, members, rules, emap = l.rstrip("\n").split("\t")
        mems = members.split(",")
        if ":H" in emap and "NEVER-HALTS" in verdicts:
            in_fw1 = [f"{m}({base_set[m]})" for m in mems if m in base_set]
            not_fw1 = [m for m in mems if m not in base_set]
            print(f"{fid:5s} (n={n:2s}) | in_fw1={in_fw1} | not_fw1={not_fw1}")
            print(f"      rules: {rules}")
            print(f"      emap : {emap}")
