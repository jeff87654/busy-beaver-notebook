import os, collections

TRIAGE = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\rcands_triage'

def read_tsv(fn):
    rows = []
    with open(os.path.join(TRIAGE, fn), 'r', encoding='utf-8') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        for l in f:
            parts = l.rstrip('\n').split('\t')
            if len(parts) == len(hdr):
                rows.append(dict(zip(hdr, parts)))
    return rows

fr_snap = read_tsv('fr_snap_triage.tsv')
sr_snap = read_tsv('sr_d4_snap_triage.tsv')
fr_ext  = read_tsv('fr_ext_triage.tsv')

print("=== 1. FR > 0 & D >= 4 in rcands_snap.tsv (100 Tier-1 families) ===")
t1_snap = [r for r in fr_snap if r['tier'] == '1']
print(f"Total Tier-1 in rcands_snap.tsv: {len(t1_snap)}")
print("  Breakdown by FR value:")
print(f"    FR >= 20 : {sum(1 for r in t1_snap if int(r['FR']) >= 20)}")
print(f"    FR 11..19: {sum(1 for r in t1_snap if 11 <= int(r['FR']) <= 19)}")
print(f"    FR 6..10 : {sum(1 for r in t1_snap if int(r['FR']) <= 10)}")
print("  All Tier-1 rows with FR >= 11 or SMALL-HALT or std_HT/max_HT >= 1 or FR2/FR3/FR46 > 0:")
for r in t1_snap:
    if int(r['FR']) >= 11 or r['small'] == 'SMALL-HALT' or int(r['max_HT']) >= 1 or int(r['FR2']) > 0 or int(r['FR3']) > 0 or int(r['FR46']) > 0:
        print(f"    {r['machine']} fam={r['family_size']} {r['small']:10s} D={r['D']:>4s}(K{r['DK']}) FR={r['FR']:>4s} SRs={r['SRs']:>4s} HT={r['std_HT']}/{r['max_HT']} nolist={r['nolist_halt']} FR2={r['FR2']} FR3={r['FR3']} FR46={r['FR46']} ref={r['FRref']} | {r['ht_details'][:70]}")

print("\n=== 2. All HT >= 2 or max_HT >= 2 in rcands_snap.tsv (FR + SR) ===")
for src, rows in [('FR_snap', fr_snap), ('SR_snap', sr_snap)]:
    for r in rows:
        if int(r['std_HT']) >= 2 or int(r['max_HT']) >= 2:
            print(f"  [{src} T{r['tier']}] {r['machine']} fam={r['family_size']} {r['small']} D={r['D']}(K{r['DK']}) SRs={r['SRs']} HT={r['std_HT']}/{r['max_HT']} nolist={r['nolist_halt']} | {r['ht_details']}")

print("\n=== 3. D >= 15 with FR2 > 0, FR3 > 0, or FR46 > 0 in rcands_snap.tsv (FR + SR) ===")
for src, rows in [('FR_snap', fr_snap), ('SR_snap', sr_snap)]:
    for r in rows:
        if int(r['D']) >= 15 and (int(r['FR2']) > 0 or int(r['FR3']) > 0 or int(r['FR46']) > 0):
            fr_val = r.get('FR', '0')
            print(f"  [{src} T{r['tier']}] {r['machine']} {r['small']:10s} D={r['D']:>4s}(K{r['DK']}) FR={fr_val:>3s} FR2={r['FR2']:>3s} FR3={r['FR3']:>3s} FR46={r['FR46']:>3s} ref={r['FRref']:>4s} pair={r['FRpair']:>4s} HT={r['std_HT']}/{r['max_HT']} nolist={r['nolist_halt']} | {r['shape'][:80]}")

print("\n=== 4. Top D >= 15 with FRref >= 20 in SR_snap (FR == 0) ===")
sr_ref = [r for r in sr_snap if int(r['D']) >= 15 and int(r['FRref']) >= 20]
sr_ref.sort(key=lambda r: (-int(r['FRref']), -int(r['D'])))
print(f"Total D>=15 SR_snap with FRref > 0: {sum(1 for r in sr_snap if int(r['D']) >= 15 and int(r['FRref']) > 0)}, with FRref >= 20: {len(sr_ref)}")
for r in sr_ref[:25]:
    print(f"  [SR_snap T{r['tier']}] {r['machine']} {r['small']:10s} D={r['D']:>4s}(K{r['DK']}) SRs={r['SRs']:>4s} ref={r['FRref']:>5s} FR2={r['FR2']} FR3={r['FR3']} pair={r['FRpair']} HT={r['std_HT']}/{r['max_HT']} nolist={r['nolist_halt']} | {r['shape'][:80]}")

print("\n=== 5. Notable FR_ext (r0017..r0105) rows with max_HT >= 2 or (D >= 15 & FR >= 50) ===")
for r in fr_ext:
    if int(r['max_HT']) >= 2 or (int(r['D']) >= 15 and int(r['FR']) >= 50):
        print(f"  [FR_ext T{r['tier']} {r['chunk']}] {r['machine']} {r['small']:10s} D={r['D']:>4s}(K{r['DK']}) FR={r['FR']:>4s} SRs={r['SRs']:>4s} HT={r['std_HT']}/{r['max_HT']} nolist={r['nolist_halt']} FR2={r['FR2']} FR3={r['FR3']} ref={r['FRref']} | {r['ht_details'][:70]}")
