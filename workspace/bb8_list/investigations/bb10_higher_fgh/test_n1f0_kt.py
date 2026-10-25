import subprocess

PKF = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_topmap_all\tools\pkf8t.exe"
FLAGS = 0x08000000 | 0x40

n1f0_per1 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI0LH_---0LC"
n1f0_per2 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_---0LI_0LE0LI"

for name, tm in [("n1f0_Per1", n1f0_per1), ("n1f0_Per2", n1f0_per2)]:
    for kt in ["1*11;1;20;0", "1*11;1;20;3", "2,1*11;1;20;0"]:
        p = subprocess.run(
            [PKF, tm, "--kt", kt, "--R", "20", "--jumps", "40", "--maxt", "1e8", "--view", "400"],
            capture_output=True, text=True, creationflags=FLAGS
        )
        print(f"=== {name} --kt {kt} ===")
        for l in p.stdout.splitlines():
            print(" ", l)
