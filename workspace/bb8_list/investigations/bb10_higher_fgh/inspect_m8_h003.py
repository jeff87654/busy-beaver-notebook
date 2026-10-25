import subprocess, os

PKF = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_topmap_all\tools\pkf8t.exe"
FLAGS = 0x08000000 | 0x40

machines = {
    "M8":   "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---",
    "M8_t1":"1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0RC---",
    "M8_t2":"1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_1RD---",
    "M8_t3":"1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0RB---",
    "M8_t4":"1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0RE---",
    "h003": "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC",
    "C7":   "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA",
    "n1f0_Per1": "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI0LH_---0LC",
    "n1f0_Per2": "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_---0LI_0LE0LI",
}

for name, tm in machines.items():
    p = subprocess.run(
        [PKF, tm, "--cnt", "--B", "66", "--cls", "66", "--mod", "150", "--jumps", "100", "--maxt", "5e8", "--view", "400"],
        capture_output=True, text=True, creationflags=FLAGS
    )
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    print(f"=== {name}: {tm} ===")
    for l in lines:
        print(" ", l)
