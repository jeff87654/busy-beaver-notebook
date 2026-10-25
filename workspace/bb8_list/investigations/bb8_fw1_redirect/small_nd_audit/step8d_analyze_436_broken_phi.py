import os, sys, collections, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"

with open(r"C:\Users\jeffr\.gemini\antigravity-cli\brain\2095fdaf-d45c-4064-998a-8aecd7858a2f\.system_generated\steps\393\output.txt", "r") as f:
    lines = f.read().splitlines()

k_mismatch = []
h_mismatch = []
t_mismatch = []

for l in lines:
    if not l.startswith("  ["):
        continue
    if "->K:" in l:
        k_mismatch.append(l)
    elif "=H:" in l:
        h_mismatch.append(l)
    else:
        t_mismatch.append(l)

print(f"Total broken_phi lines: {len(k_mismatch) + len(h_mismatch) + len(t_mismatch)}")
print(f"  With K: parity mismatch (->K:): {len(k_mismatch)}")
print(f"  With H: halt on D/B/LB (=H:)  : {len(h_mismatch)}")
print(f"  With T timeout only (=T)      : {len(t_mismatch)}")

print("\n=== All leaves with K: parity mismatch (->K:) ===")
for l in k_mismatch:
    print(l)
