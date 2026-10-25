import os

out_file = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade\partB_screen_xh0914.out.txt"

with open(out_file, "r") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total lines: {len(lines)}")

mixed = []
clean_K_with_halt_slot = []
any_H_rows = []

for l in lines:
    if l.startswith("DONE:"):
        print(l)
        continue
    # format: [9st xh_0914 H0=0LI I=---0LA] k2=...
    hdr, rest = l.split("] ", 1)
    hdr = hdr[1:]
    has_halt_slot = ("---" in hdr)
    items = rest.strip().split()
    kinds = [it.split("=")[1][0] for it in items]
    has_k = any(c in ('K', 'k') for c in kinds)
    has_h = any(c in ('H', 'h') for c in kinds)
    if has_h:
        any_H_rows.append((hdr, rest))
    if has_k and has_h:
        mixed.append((hdr, rest))
    if has_k and has_halt_slot and all(c == 'K' for c in kinds):
        clean_K_with_halt_slot.append((hdr, rest))

print(f"\nRows with any H/h: {len(any_H_rows)}")
for hdr, rest in any_H_rows[:30]:
    print(f"  [{hdr}] {rest}")

print(f"\nMIXED_KH rows: {len(mixed)}")
for hdr, rest in mixed:
    print(f"  [{hdr}] {rest}")

print(f"\nAll-K (c=0) rows that STILL have a --- halt slot in I: {len(clean_K_with_halt_slot)}")
for hdr, rest in clean_K_with_halt_slot:
    print(f"  [{hdr}] {rest}")
