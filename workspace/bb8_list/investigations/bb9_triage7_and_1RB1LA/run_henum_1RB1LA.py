import sys, os, subprocess, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'henum_1RB1LA_9.exe')
OUT = os.path.join(HERE, 'henum_1RB1LA_9.tsv')

VARIANTS = [
    ("V0_H1_0LB", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LB"),
    ("V1_H1_0LD", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LD"),
    ("V2_H1_1LE", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---1LE"),
    ("V3_G0_1RH_0LA", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_1RH0RF_---0LA"),
    ("V4_G0_1RH_0LG", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_1RH0RF_---0LG"),
    ("V5_G0_1RH_1RB", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_1RH0RF_---1RB"),
    ("V6_E0_0RH_0LB", "1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RH0LC_0LD0RG_0RH0RF_---0LB"),
]

with open(OUT, 'w', encoding='utf-8') as fo:
    for vname, tm in VARIANTS:
        t0 = time.time()
        p = subprocess.Popen([EXE, tm, '100000', '50000'], creationflags=0x40, stdout=subprocess.PIPE, text=True)
        with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
            pf.write(f"henum_1RB1LA_9 {vname} {p.pid}\n")
        out, _ = p.communicate()
        dt = time.time() - t0
        fo.write(f"#variant {vname} {tm} ({dt:.1f}s)\n")
        fo.write(out)
        fo.flush()
        lines = out.splitlines()
        summary = [l for l in lines if l.startswith('#summary')]
        print(f"{vname}: {len(lines)-1} interesting lines in {dt:.1f}s | {summary[0] if summary else ''}", flush=True)
