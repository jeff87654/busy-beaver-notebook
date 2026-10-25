import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter

def short_verdict(v):
    if v.startswith('NOT-RECORD-CLASS'):
        return v.split(')')[0] + ')'
    return v.split('(')[0].split('+')[0]

with open('census12_all.tsv') as f:
    header = f.readline().rstrip('\n').split('\t')
    rows = [dict(zip(header, line.rstrip('\n').split('\t'))) for line in f if line.strip()]

print("=== EXACT <=12 TRANSITIONS USED AFTER STEP 5,000 (n_used_after_5k <= 12) ===")
after5k_le12 = [r for r in rows if int(r['n_used_after_5k']) <= 12]
print(f"Total across all 1,797 machines: {len(after5k_le12)}")
print("By verdict:", dict(Counter(short_verdict(r['verdict']) for r in after5k_le12)))
print("By (verdict, n_used_after_5k):", dict(Counter((short_verdict(r['verdict']), int(r['n_used_after_5k'])) for r in after5k_le12)))

non_low = [r for r in after5k_le12 if 'LOW-GROWTH' not in r['verdict']]
print(f"\nNon-low-growth machines with n_used_after_5k <= 12: {len(non_low)}")

# Separate slots with 0 executions after 5k into STARTUP_ONLY vs EARLY_ONLY(EXH) vs UNUSED
zero_after_5k_roles = Counter()
for r in non_low:
    for item in r['non_engine_slots'].split(';'):
        if ':' in item:
            slot, role = item.split(':', 1)
            if role.startswith(('STARTUP_ONLY', 'EARLY_ONLY', 'UNUSED')):
                zero_after_5k_roles[role.split('(')[0]] += 1
print("Zero-after-5k slot roles in non-low-growth:", dict(zero_after_5k_roles))

print("\n--- All HALTS (HALT-REACHED / HALTS-SMALL) with n_used_after_5k <= 12 ---")
for r in non_low:
    if 'HALT' in short_verdict(r['verdict']) and not short_verdict(r['verdict']).startswith('NEVER'):
        zslots = [x for x in r['non_engine_slots'].split(';') if any(k in x for k in ('STARTUP_ONLY', 'EARLY_ONLY', 'UNUSED'))]
        print(f"  {r['machine']} | {r['grade']} | {r['verdict'][:40]} | after5k={r['n_used_after_5k']} | {';'.join(zslots)}")

print("\n--- Sample NEVER-HALTS with n_used_after_5k == 11 (2 free slots after 5k!) ---")
nh11 = [r for r in non_low if int(r['n_used_after_5k']) == 11]
print(f"Count of non-low-growth with n_used_after_5k == 11: {len(nh11)}")
for r in nh11[:25]:
    zslots = [x for x in r['non_engine_slots'].split(';') if any(k in x for k in ('STARTUP_ONLY', 'EARLY_ONLY', 'UNUSED'))]
    print(f"  {r['machine']} | {r['grade']} | {short_verdict(r['verdict'])} | {';'.join(zslots)} | {r['exhaustion'][:50]}")

# Check X33 specifically
for r in rows:
    if r['machine'] in (
        '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE',
        '1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB',
        '1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF',
    ):
        print("\nControl machine:", r['machine'])
        print("  verdict:", r['verdict'])
        print("  after5k:", r['n_used_after_5k'], "after100k:", r['n_used_after_100k'], "eng:", r['n_engine'])
        print("  non_engine_slots:", r['non_engine_slots'])
