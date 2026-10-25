import os, sys

REB7_FAM = r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\final_all_families.tsv"
FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
sys.path.insert(0, FW1_DIR)
from bcfg import BASES

def sim_used_slots(m_str, max_steps=100000):
    parts = m_str.split("_")
    n_states = len(parts)
    trans = {}
    undef = []
    for s_idx, p in enumerate(parts):
        for sym in (0, 1):
            cell = p[3*sym : 3*sym+3]
            if cell == "---":
                undef.append(f"{chr(65+s_idx)}{sym}")
                trans[(s_idx, sym)] = None
            else:
                w = int(cell[0])
                mv = 1 if cell[1] == "R" else -1
                ns = ord(cell[2]) - 65
                trans[(s_idx, sym)] = (w, mv, ns)
    tape = {}
    head = 0
    state = 0
    used = set()
    for step in range(max_steps):
        sym = tape.get(head, 0)
        used.add(f"{chr(65+state)}{sym}")
        t = trans[(state, sym)]
        if t is None:
            return used, undef, f"HALT@{step}"
        w, mv, ns = t
        tape[head] = w
        head += mv
        state = ns
    return used, undef, "RUN"

target_fids = ["F1", "F2", "F5", "F13", "F14", "F15", "F18", "F19", "F20", "F44", "F51", "F70", "F86", "F89", "F141", "F198", "F231", "F232", "F251", "F277", "F278", "F279", "F385", "F399"]
fams = {}
with open(REB7_FAM, "r") as f:
    f.readline()
    for l in f:
        if not l.strip():
            continue
        p = l.rstrip("\n").split("\t")
        fams[p[0]] = p

for fid in target_fids:
    p = fams[fid]
    rep = p[1]
    used, undef, st = sim_used_slots(rep, 50000)
    print(f"{fid:5s} (n={p[2]:3s}) rep={rep} | undef={undef} | n_used={len(used)} ({sorted(used)})")
    print(f"      rules: {p[6]}")
    print(f"      emap : {p[7]}")
