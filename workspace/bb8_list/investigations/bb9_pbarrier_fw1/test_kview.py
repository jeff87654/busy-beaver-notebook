import os, sys, subprocess
os.environ["PATH"] = r"C:\msys64\ucrt64\bin;" + os.environ.get("PATH", "")
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

for name, m, t_str in [
    ("M4_1010", "1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_1RA1RE", "L,C,P=1010,u=01,s=0,d=1d+0,b=1b+0,S=-"),
    ("M4_1", "1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_1RA1RE", "L,C,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-"),
    ("NEW_MULTI", "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF", "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1"),
]:
    T = kl.tmpl(m, t_str)
    cmd = [kl.EXE, m] + kl.args(T) + ["100000", "30", "0"]
    p = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    print(f"=== {name} ===")
    print(p.stdout[:1000])
