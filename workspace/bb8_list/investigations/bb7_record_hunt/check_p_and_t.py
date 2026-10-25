import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import subprocess, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
RK7 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'

rows = []
with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\audit_out.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        parts = line.rstrip('\n').split('\t')
        rows.append(dict(zip(hdr, parts)))

# Check all rows with patL in PPPPPPPPPPPP or TTTTTTTTTTTT
pt_rows = [r for r in rows if r['patL'] in ('PPPPPPPPPPPP', 'TTTTTTTTTTTT', 'KHPKHPKHPKHP')]
print(f"Total P/T rows to inspect: {len(pt_rows)}")

for i, r in enumerate(pt_rows):
    m = r['machine']
    g = r['grade']
    ts = r['tmpl'].split(',')
    o, q = ts[0], ts[1]
    kv = {x.split('=')[0]: x.split('=')[1] for x in ts[2:]}
    u, s, S = kv['u'], kv['s'], kv['S']
    # Test with P='-' and al=1, be=0, alB=1, beB=0
    t_raw = [o, q, '-', u, s, '1', '0', '1', '0', S]
    # Trace from blank tape for 2M steps, 50 K-configs
    p = subprocess.run([RK7, 'trace', m] + t_raw + ['2000000', '50'], capture_output=True, text=True, creationflags=0x40)
    tlines = [x for x in p.stdout.strip().splitlines() if x.startswith('K ')]
    endline = [x for x in p.stdout.strip().splitlines() if not x.startswith('K ')]
    # Probe E(b) = K(; 0; b) for b = 10..21 in t_raw
    cfgs = f"- 0 10\n- 0 11\n- 0 12\n- 0 13\n- 0 14\n- 0 15\n- 0 16\n- 0 17\n"
    p2 = subprocess.run([RK7, 'probe', m] + t_raw + ['300000'], input=cfgs, capture_output=True, text=True, creationflags=0x40)
    plines = [x.split()[0] for x in p2.stdout.strip().splitlines()]
    pat_raw = ''.join(plines)
    last_k = tlines[-1] if tlines else '-'
    print(f"{i+1:2d}. {g:10s} {m} | orig={r['tmpl']:35s} | raw_E(10..17)={pat_raw:8s} | nk={len(tlines):2d} last={last_k[:55]} | end={endline}")
