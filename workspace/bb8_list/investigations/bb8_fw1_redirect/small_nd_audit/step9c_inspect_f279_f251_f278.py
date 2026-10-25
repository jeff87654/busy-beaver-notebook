import os, sys, glob, json

REB7_DIR = r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7"
REB7_FAM = os.path.join(REB7_DIR, "final_all_families.tsv")

target_fids = {"F1", "F2", "F5", "F44", "F51", "F70", "F86", "F89", "F141", "F198", "F231", "F251", "F277", "F278", "F279", "F385", "F399"}
rep_to_fid = {}
with open(REB7_FAM, "r") as f:
    f.readline()
    for l in f:
        if not l.strip():
            continue
        p = l.rstrip("\n").split("\t")
        if p[0] in target_fids:
            rep_to_fid[p[1]] = p[0]

for jfn in sorted(glob.glob(os.path.join(REB7_DIR, "run_*.jsonl"))):
    with open(jfn, "r") as f:
        for l in f:
            if not l.strip():
                continue
            d = json.loads(l)
            m = d.get("machine")
            if m in rep_to_fid:
                fid = rep_to_fid[m]
                print(f"=== {fid}: {m} (from {os.path.basename(jfn)}) ===")
                print("  tmpl   :", d.get("tmpl"))
                print("  rules  :", d.get("rules"))
                print("  E0     :", d.get("E0"), "| E0_pat:", d.get("E0_pat", "")[:16])
                print("  inv    :", d.get("invariant"), "|", d.get("inv_detail"))
                print("  verdict:", d.get("verdict"), "| lit_exh:", d.get("lit_exh"))
