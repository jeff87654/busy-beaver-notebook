import os, sys, json, ctypes
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl
from build_and_profile_parents import run_from_k, parse_k

def set_slots(M, slot_map):
    rows = [list(r) for r in M.split('_')]
    for s, val in slot_map.items():
        q = ord(s[0]) - 65
        c = int(s[1])
        rows[q][3*c:3*c+3] = list(val)
    return '_'.join(''.join(r) for r in rows)

ALL_TR = [f"{w}{d}{ chr(65+q) }" for w in (0, 1) for d in ('L', 'R') for q in range(8)]

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\parents_profile.json') as f:
    parents = {p['id']: p for p in json.load(f)}

def scan_e_slots(pid, free_slots, b_vals=range(10, 22)):
    p = parents[pid]
    M0 = p['machine']
    t = kl.tmpl(M0, p['tmpl_str'])
    nE = p['nE']
    print(f"=== Scanning {pid} free_slots={free_slots} (tmpl={p['tmpl_str']}, nE={nE}) ===")
    # If 2 slots: one is '---', the other in ALL_TR (2 * 32 = 64)
    # If 3 slots (e.g. G0, H0, H1): either G0 -> w d H and one of (H0, H1) in ALL_TR, other '---'
    # OR one of the 3 slots is '---' and the other 2 are in ALL_TR (3 * 32 * 32 = 3072)
    cands = []
    if len(free_slots) == 2:
        s0, s1 = free_slots
        for tr in ALL_TR:
            cands.append({s0: '---', s1: tr})
            cands.append({s0: tr, s1: '---'})
    elif len(free_slots) == 3:
        # free_slots = [entry_slot, stateX_0, stateX_1] where stateX is only reached via entry_slot
        entry, x0, x1 = free_slots
        x_state = x0[0]
        # Case 1: entry goes to x_state (4 choices), one of (x0, x1) is '---', other in ALL_TR (2 * 32 = 64)
        for w in (0, 1):
            for d in ('L', 'R'):
                etr = f"{w}{d}{x_state}"
                for tr in ALL_TR:
                    cands.append({entry: etr, x0: tr, x1: '---'})
                    cands.append({entry: etr, x0: '---', x1: tr})
        # Case 2: entry goes to another state (28 choices), x0='---', x1='---'
        for tr in ALL_TR:
            if tr[2] != x_state:
                cands.append({entry: tr, x0: '---', x1: '---'})

    print(f"  Testing {len(cands)} slot assignments on E(b={list(b_vals)})...")
    mixed_hits = []
    for sm in cands:
        M = set_slots(M0, sm)
        # First quick test on b=12, 13, 14, 15
        kinds = []
        outs = []
        for b in (12, 13, 14, 15):
            knd, r, _, st = run_from_k(M, t, [0]*nE, 0, b, maxs=15000)
            kinds.append(knd)
            outs.append((b, knd, r))
        if 'K' in kinds and 'H' in kinds:
            # Test full b_vals
            full_outs = []
            for b in b_vals:
                knd, r, _, st = run_from_k(M, t, [0]*nE, 0, b, maxs=25000)
                full_outs.append((b, knd, r))
            pat = ''.join(x[1] for x in full_outs)
            k_lens = [len(x[2][0]) for x in full_outs if x[1] == 'K']
            if max(k_lens, default=0) >= 8:
                mixed_hits.append((sm, M, pat, full_outs))
    print(f"  Found {len(mixed_hits)} MIXED (K+H with growing K) exhaustion maps!")
    for sm, M, pat, full_outs in mixed_hits[:25]:
        det = ' '.join(f"{b}:{k}({len(r[0])};{r[1]};{r[2]})" if k=='K' else f"{b}:{k}" for b, k, r in full_outs[:8])
        print(f"    {sm} -> pat={pat} | {det}")
    return mixed_hits

scan_e_slots('pool8_13', ['G0', 'H0', 'H1'])
scan_e_slots('pool8_02', ['C0', 'D0', 'D1'])
scan_e_slots('pool8_18', ['B0', 'C0', 'C1'])
scan_e_slots('pool8_01', ['C1', 'H0'])
scan_e_slots('pool8_06', ['B0', 'D0', 'H0'])
scan_e_slots('pool8_09', ['D0', 'E0'])
