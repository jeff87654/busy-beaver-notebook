import subprocess

PKF = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_topmap_all\tools\pkf8t.exe"
FLAGS = 0x08000000 | 0x40

h003 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0LI---_1RI1RC"

for k in range(50, 55):
    kt = f"0*2,1*{k+1};1;200;3"
    p = subprocess.run(
        [PKF, h003, "--cnt", "--kt", kt, "--B", "66", "--cls", "66", "--mod", "150", "--jumps", "30", "--maxs", "5e7", "--maxt", "2e8", "--view", "400"],
        capture_output=True, text=True, creationflags=FLAGS
    )
    print(f"=== h003 on Top K={k} (K%5={k%5}) ===")
    for l in p.stdout.splitlines():
        print(" ", l)
