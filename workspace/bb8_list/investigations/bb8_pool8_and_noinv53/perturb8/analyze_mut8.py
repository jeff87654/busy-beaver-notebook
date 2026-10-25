import collections

for fn in ['scan_mut8_cls53.tsv', 'scan_mut8_cand162.tsv']:
    path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\\' + fn
    pstats = collections.Counter()
    epats = collections.Counter()
    interesting = []
    total = 0
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='ignore')
    for line in text.splitlines():
            parts = line.rstrip('\r\n').split('\t')
            if len(parts) < 9:
                continue
            total += 1
            pid, grp, tag_info, mstr, epat, pstat, binfo, btrace, details = parts[:9]
            pstats[pstat] += 1
            epats[epat] += 1
            # Parse nE and maxL from binfo: e.g. T:400000:nK=12:nE=2:maxL=55
            bdict = {}
            for kv in binfo.split(':')[2:]:
                if '=' in kv:
                    k, v = kv.split('=')
                    bdict[k] = int(v)
            maxL = bdict.get('maxL', 0)
            nE = bdict.get('nE', 0)
            if pstat != 'LOCKED_A_PAR' and (maxL >= 8 or nE >= 2 or pstat in ('B_DEP_A_PAR!', 'NON_MOD2_E!')):
                interesting.append((pstat, maxL, nE, pid, grp, tag_info, mstr, epat, binfo, btrace, details))

    print(f"=== {fn}: total={total} ===")
    print("  pstats:", dict(pstats))
    print("  epats:", dict(epats))
    print(f"  interesting (not LOCKED_A_PAR, maxL>=8 or nE>=2 or special): {len(interesting)}")
    for item in sorted(interesting, reverse=True)[:40]:
        pstat, maxL, nE, pid, grp, tag_info, mstr, epat, binfo, btrace, details = item
        print(f"    [{pstat:12s}] maxL={maxL:3d} nE={nE:2d} | {pid:16s} {tag_info:16s} | {epat} | {btrace[:35]:35s} | {details[:90]}")
