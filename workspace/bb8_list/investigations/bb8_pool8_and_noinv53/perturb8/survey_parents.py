import os, sys, json, re, ctypes
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl

# 1. Load cls53 verdicts
verdicts_path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\noinv53_verdicts.tsv'
cls53_parents = []
with open(verdicts_path) as f:
    hdr = f.readline()
    for line in f:
        parts = line.rstrip('\n').split('\t')
        idx = int(parts[0])
        tag = parts[1]
        m = parts[2]
        fam = parts[3]
        verd = parts[4]
        scale = parts[5]
        btrace = parts[6]
        note = parts[7]
        if 'FOMEGA' in scale or 'TETRATIONAL' in scale:
            _, tmpl_str, B0, _ = bcfg.BASES[tag]
            cls53_parents.append({
                'id': f'cls53_{idx:02d}_{tag}',
                'machine': m,
                'tmpl_str': tmpl_str,
                'B0': B0,
                'family': fam,
                'verdict': verd,
                'scale': scale,
                'btrace': btrace
            })

# 2. Load pool8.tsv and run8.jsonl
pool8_parents = []
run8_path = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\run8.jsonl'
with open(run8_path) as f:
    for i, line in enumerate(f, 1):
        d = json.loads(line)
        m = d['machine']
        verd = d.get('verdict', '')
        tmpl_str = d.get('tmpl') or d.get('tmpl_in')
        if i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 21, 23):
            pool8_parents.append({
                'id': f'pool8_{i:02d}',
                'machine': m,
                'tmpl_str': tmpl_str,
                'B0': 0,
                'family': f'pool8_r{i}',
                'verdict': verd,
                'scale': d.get('growth', 'FOMEGA'),
                'btrace': str(d.get('first_K', ''))
            })

# 3. Also check bb8_fw1_redirect for intact/modified KHKH leaves with big rebuilds
fw1_extra = []
noinv_blank_path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\noinv_blank.tsv'
cls53_set = {p['machine'] for p in cls53_parents}
with open(noinv_blank_path) as f:
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) >= 6:
            tag, m, st, nK, nE, max_len = parts[:6]
            ev = parts[6] if len(parts) > 6 else ''
            if int(max_len) >= 10 and m not in cls53_set:
                _, tmpl_str, B0, _ = bcfg.BASES[tag]
                fw1_extra.append({
                    'id': f'fw1_noinv_{tag}_{len(fw1_extra):02d}',
                    'machine': m,
                    'tmpl_str': tmpl_str,
                    'B0': B0,
                    'family': f'fw1_{tag}',
                    'verdict': st,
                    'scale': f'max_len={max_len}',
                    'btrace': ev.strip()
                })

print(f"cls53 Ackermann/Tetrational parents: {len(cls53_parents)}")
print(f"pool8 parents: {len(pool8_parents)}")
print(f"fw1_extra (noinv_blank max_len>=10 not in cls53): {len(fw1_extra)}")
for p in fw1_extra[:15]:
    print(" ", p['id'], p['machine'], p['scale'], p['btrace'][:60])
