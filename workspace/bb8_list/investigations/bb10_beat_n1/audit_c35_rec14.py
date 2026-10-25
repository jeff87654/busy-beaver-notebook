"""Audit all 60 UNCLEAR-MAXSTAGES + 4 UNCLEAR-T + 2 looper machines in c35m14, and all MAXSTAGES / level>=2 machines in rec14, by parsing their detailed stage logs in bb10_bb7_descendants/logs/."""
import os, glob, re
from pathlib import Path

DESC_DIR = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_bb7_descendants')
LOGS_DIR = DESC_DIR / 'logs'
OUT_DIR = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_beat_n1')

def parse_log(log_path):
    if not log_path.exists():
        return None
    lines = log_path.read_text(errors='replace').splitlines()
    stages = []
    cur = {}
    res_line = None
    for l in lines:
        if l.startswith('stage '):
            if cur:
                stages.append(cur)
            cur = {'header': l}
        elif 'champion phase' in l:
            cur['champ'] = l.strip()
        elif 'jump ->' in l:
            cur['jump'] = l.strip()
        elif 'event config:' in l:
            cur['event'] = l.strip()
        elif 'HALT' in l and not l.startswith('RESULT'):
            cur['halt'] = l.strip()
        elif l.startswith('RESULT '):
            res_line = l.strip()
    if cur:
        stages.append(cur)
    return {'stages': stages, 'result': res_line}

def main():
    out = []
    c35_lines = (DESC_DIR / 'results_c35.tsv').read_text().splitlines()
    out.append(f"Total rows in results_c35.tsv: {len(c35_lines)}")
    non_halt = []
    for l in c35_lines:
        parts = l.split('\t')
        m, tag, res = parts[0], parts[1], parts[2]
        if not res.startswith('RESULT HALT'):
            non_halt.append((m, tag, res))
    out.append(f"Non-HALT rows in results_c35.tsv: {len(non_halt)}")

    groups = {}
    for m, tag, res in non_halt:
        lp = LOGS_DIR / f"{m}.log"
        info = parse_log(lp)
        if not info or not info['stages']:
            key = ('NO_LOG', res)
        else:
            st0 = info['stages'][0]
            ch0 = st0.get('champ', 'NO_CHAMP')
            ev0 = st0.get('event', 'NO_EVENT')
            key = (ch0, ev0)
        groups.setdefault(key, []).append((m, res, info))

    out.append(f"\nGrouped {len(non_halt)} non-HALT c35m14 machines into {len(groups)} stage-0 patterns:")
    for i, ((ch0, ev0), items) in enumerate(sorted(groups.items(), key=lambda x: -len(x[1])), 1):
        out.append(f"\n--- Group {i}: {len(items)} machines ---")
        out.append(f"  Stage 0 champ: {ch0}")
        out.append(f"  Stage 0 event: {ev0}")
        ex_m, ex_res, ex_info = items[0]
        out.append(f"  Example machine: {ex_m}")
        out.append(f"  Result: {ex_res}")
        if ex_info:
            for s in ex_info['stages']:
                out.append(f"    {s.get('header')} -> {s.get('event', s.get('champ', ''))}")
        out.append("  Machines in group:")
        for m, res, _ in items:
            out.append(f"    {m}  [{res.split(' history=')[0]}]")

    # Also check rec14 MAXSTAGES and level >= 2 machines
    out.append("\n" + "="*80)
    out.append("REC14 & REC14_0RH MAXSTAGES AND LEVEL >= 2 MACHINES")
    out.append("="*80)
    rec_files = ['results_r1.tsv', 'results_reps.tsv', 'results_cls.tsv', 'results_mem.tsv', 'results_0RH.tsv', 'results_sib.tsv', 'results_redo.tsv']
    seen_rec = {}
    for rf in rec_files:
        p = DESC_DIR / rf
        if not p.exists():
            continue
        for l in p.read_text(errors='replace').splitlines():
            parts = l.split('\t')
            if len(parts) < 3:
                continue
            m, tag, res = parts[0], parts[1], parts[2]
            if '[by class]' in res:
                continue
            seen_rec[m] = (rf, tag, res)

    interesting_rec = []
    for m, (rf, tag, res) in seen_rec.items():
        if 'MAXSTAGES' in res or 'level=2' in res or 'level=3' in res or 'full_cycles=2' in res or 'full_cycles=3' in res or 'full_cycles=4' in res or 'full_cycles=6' in res or 'full_cycles=8' in res:
            if not res.startswith('RESULT LOOP'):
                interesting_rec.append((m, rf, tag, res))

    out.append(f"Found {len(interesting_rec)} non-LOOP rec14/0RH machines with MAXSTAGES or full_cycles>=2 or level>=2:")
    for m, rf, tag, res in sorted(interesting_rec, key=lambda x: (x[1], x[0])):
        out.append(f"\n  Machine: {m} ({rf}, {tag})")
        out.append(f"  Result:  {res}")
        lp = LOGS_DIR / f"{m}.log"
        info = parse_log(lp)
        if info:
            for s in info['stages']:
                out.append(f"    {s.get('header')} | {s.get('jump', '')} -> {s.get('event', s.get('champ', ''))}")

    (OUT_DIR / 'c35_rec14_audit.txt').write_text('\n'.join(out), encoding='utf-8')
    print(f"Wrote {len(out)} lines to c35_rec14_audit.txt")

if __name__ == '__main__':
    main()
