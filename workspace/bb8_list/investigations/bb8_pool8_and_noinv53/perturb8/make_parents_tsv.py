import json

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\parents_profile.json') as f:
    parents = json.load(f)

# Deduplicate parents by (machine, tmpl_str) while keeping all cls53 and pool8 machines
out = []
seen = set()
for p in parents:
    if p['source'] in ('cls53', 'pool8') or p['machine'] not in seen:
        seen.add(p['machine'])
        out.append(p)

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\parents_scan.tsv', 'w') as f:
    for p in out:
        # id, source, group, machine, tmpl_str, B0, nE, mode, undef, D_used, B_only, E_only, start_only, unused_all
        f.write('\t'.join([
            p['id'],
            p['source'],
            p['group'],
            p['machine'],
            p['tmpl_str'],
            str(p['B0']),
            str(p['nE']),
            p['mode'],
            ','.join(p['undef']) or '-',
            ','.join(p['D_used']) or '-',
            ','.join(p['B_only']) or '-',
            ','.join(p['E_only']) or '-',
            ','.join(p['start_only']) or '-',
            ','.join(p['unused_all']) or '-',
        ]) + '\n')

print(f"Wrote {len(out)} parents to parents_scan.tsv")
