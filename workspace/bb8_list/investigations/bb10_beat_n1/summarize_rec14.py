"""Summarize all 189 non-LOOP rec14 / rec14_0RH machines from c35_rec14_audit.txt by outcome and stage pattern."""
from pathlib import Path
import re

txt = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_beat_n1\c35_rec14_audit.txt').read_text(encoding='utf-8')
rec_sec = txt.split('REC14 & REC14_0RH MAXSTAGES AND LEVEL >= 2 MACHINES')[1]

blocks = rec_sec.split('\n  Machine: ')[1:]
print(f"Total rec14 / rec14_0RH blocks: {len(blocks)}")

by_status = {}
by_pattern = {}
halts = []
for b in blocks:
    lines = b.strip().splitlines()
    m_line = lines[0]
    m = m_line.split()[0]
    src = m_line.split('(')[1].rstrip(')')
    res_line = lines[1].strip()
    m_res = re.search(r'RESULT (\S+) stages=(\d+) full_cycles=(\d+) level=(\d+)', res_line)
    status, st, fc, lvl = m_res.groups() if m_res else ('?', '?', '?', '?')
    by_status[(src, status, f"lvl={lvl}")] = by_status.get((src, status, f"lvl={lvl}"), 0) + 1
    if status == 'HALT':
        halts.append((m, src, res_line, lines[2:]))
    # Pattern: stage 0 and last stage event config
    st_configs = [l.split('-> event config: ')[-1] for l in lines[2:] if '-> event config: ' in l]
    pat = (status, f"lvl={lvl}", st_configs[0] if st_configs else '', st_configs[-1] if st_configs else '')
    by_pattern.setdefault(pat, []).append(m)

print("\nBreakdown by (source, status, level):")
for k, v in sorted(by_status.items()):
    print(f"  {str(k):55s}: {v}")

print(f"\nHalting machines in rec14/0RH with level>=2 or full_cycles>=2 ({len(halts)}):")
for m, src, rl, stlines in halts:
    print(f"  {m} ({src}): {rl}")
    for sl in stlines:
        print(f"    {sl.strip()}")

print(f"\nDistinct (status, level, stage0_cfg, last_cfg) patterns ({len(by_pattern)}):")
for (status, lvl, s0, slast), ms in sorted(by_pattern.items(), key=lambda x: -len(x[1])):
    print(f"  count={len(ms):3d} | {status:10s} {lvl} | s0={s0} -> last={slast} | ex={ms[0]}")
