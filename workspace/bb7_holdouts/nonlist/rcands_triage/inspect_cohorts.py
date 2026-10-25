import os, glob, collections

NONLIST = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
TRIAGE = os.path.join(NONLIST, 'rcands_triage')

def analyze_cands(path, label):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for l in f:
            if l.startswith(('class', '#')): continue
            parts = l.rstrip('\n').split('\t')
            if len(parts) >= 13:
                rows.append(parts)
    fr_rows = [r for r in rows if r[0] == 'FR']
    sr_rows = [r for r in rows if r[0] == 'SR']
    print(f"=== {label} ({len(rows)} families, {sum(int(r[2]) for r in rows)} machines) ===")
    print(f"  FR class (FR > 0): {len(fr_rows)} families ({sum(int(r[2]) for r in fr_rows)} machines)")
    print(f"    SRs >= 20: {sum(1 for r in fr_rows if int(r[6]) >= 20)}, SRs >= 10: {sum(1 for r in fr_rows if int(r[6]) >= 10)}, SRs 4..9: {sum(1 for r in fr_rows if int(r[6]) < 10)}")
    print(f"    FR >= 100: {sum(1 for r in fr_rows if int(r[11]) >= 100)}, FR 20..99: {sum(1 for r in fr_rows if 20 <= int(r[11]) < 100)}, FR 6..19: {sum(1 for r in fr_rows if int(r[11]) < 20)}")
    print(f"  SR class (FR == 0, SRs >= 10): {len(sr_rows)} families ({sum(int(r[2]) for r in sr_rows)} machines)")
    print(f"    SRs >= 100: {sum(1 for r in sr_rows if int(r[6]) >= 100)}, SRs 30..99: {sum(1 for r in sr_rows if 30 <= int(r[6]) < 100)}, SRs 15..29: {sum(1 for r in sr_rows if 15 <= int(r[6]) < 30)}, SRs 10..14: {sum(1 for r in sr_rows if int(r[6]) < 15)}")
    return rows, fr_rows, sr_rows

snap_rows, snap_fr, snap_sr = analyze_cands(os.path.join(TRIAGE, 'rcands_snap.tsv'), 'rcands_snap.tsv (chunks r0000..r0016)')
all_rows, all_fr, all_sr = analyze_cands(os.path.join(TRIAGE, 'rcands_rfull_all.tsv'), 'rcands_rfull_all.tsv (chunks r0000..r0105)')

# Also check rpil/r0000.tsv .. r0106.tsv summary
rpil_files = sorted(glob.glob(os.path.join(NONLIST, 'rpil', 'r*.tsv')))
done_rpil = []
for p in rpil_files:
    with open(p, 'rb') as f:
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 300))
        if b'#summary' in f.read():
            done_rpil.append(p)

tot_m = 0
pass_both = 0
pass_p2_only = 0
pass_nsr_only = 0
halt_pil = 0
for p in done_rpil:
    for l in open(p, 'r', encoding='utf-8', errors='replace'):
        if l.startswith(('#', 'machine')): continue
        x = l.rstrip('\n').split('\t')
        if len(x) < 11: continue
        tot_m += 1
        p2 = float(x[3])
        nsr = int(x[9])
        if p2 == 99.0: halt_pil += 1
        if p2 >= 8.0 and nsr >= 2: pass_both += 1
        elif p2 >= 8.0: pass_p2_only += 1
        elif nsr >= 2: pass_nsr_only += 1

tot_pass = pass_both + pass_p2_only + pass_nsr_only
print(f"\n=== Stage A (rpil) across {len(done_rpil)} completed chunks ({os.path.basename(done_rpil[0])}..{os.path.basename(done_rpil[-1])}) ===")
print(f"  Total pf7-rejected holdouts scanned: {tot_m:,}")
print(f"  Gate passers (P2 >= 8.0 | nsr >= 2): {tot_pass:,} ({100*tot_pass/max(tot_m,1):.2f}%)")
print(f"    P2 >= 8.0 & nsr >= 2 : {pass_both:,}")
print(f"    P2 >= 8.0 & nsr < 2  : {pass_p2_only:,}")
print(f"    P2 < 8.0  & nsr >= 2 : {pass_nsr_only:,} (slow-start slot-reset passers)")
print(f"    Halted in 300k macro : {halt_pil:,}")
