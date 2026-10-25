import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import subprocess, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
RK7 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'

def follow(m, t_args, ds, a, b, N=1000000, maxp=8):
    s = f"{','.join(map(str, ds)) if ds else '-'} {a} {b}\n"
    p = subprocess.run([RK7, 'follow', m] + t_args + [str(N), str(maxp)], input=s, capture_output=True, text=True, creationflags=0x40)
    return p.stdout.strip().splitlines()

def trace(m, t_args, steps=5000000, maxk=30):
    p = subprocess.run([RK7, 'trace', m] + t_args + [str(steps), str(maxk)], capture_output=True, text=True, creationflags=0x40)
    return p.stdout.strip().splitlines()

print("=== Check Row 50: 1RB1RD_1LC0RD_0LG1LD_1RA0RE_1LF1LA_0LC1LE_---0LE ===")
m50 = "1RB1RD_1LC0RD_0LG1LD_1RA0RE_1LF1LA_0LC1LE_---0LE"
for l in trace(m50, ['R','A','111','10','1','1','0','1','0','1'], 500000, 20):
    print(" ", l)
print("Follow from K(0,0; 0; 20) in P=111:")
for l in follow(m50, ['R','A','111','10','1','1','0','1','0','1'], [0,0], 0, 20, 500000, 10):
    print(" ", l)

print("\n=== Check Row 12 (representative of TKTKTKTK group: P=10,u=1,s=0,d=2d+0,b=2b+1,S=11) ===")
m12 = "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB"
for b in range(10, 16):
    print(f"  b={b} (raw u=1,s=0,P=-):", follow(m12, ['L','E','-','1','0','1','0','1','0','11'], [], 0, b, 200000, 3))

print("\n=== Check Row 3 (representative of P=110,u=01,s=0 group) ===")
m3 = "1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG1RA_1LE1RE"
# In P=110, u=01, s=0, at exhaustion of P=11 (ds=0^10), it went to P=1, ds=[29, 1^9], a=1, b=1.
# What happens when P=1, ds=0^10 exhausts?!
for b in (20, 21, 22, 23):
    print(f"  P=1, ds=0^5, b={b}:", follow(m3, ['L','C','1','01','0','1','0','1','0','-'], [0]*5, 0, b, 500000, 5))

print("\n=== Check Row 10 (representative of P=10,u=01,s=0,d=2d+0 group) ===")
m10 = "1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB"
for b in (20, 21, 22, 23):
    print(f"  P=1, ds=0^5, b={b}:", follow(m10, ['R','C','1','01','0','2','0','2','1','0'], [0]*5, 0, b, 500000, 5))

print("\n=== Check Row 56 (CHAMPION 1RB0RB_1RC1RG_1LD---_1RA1LE_0RF0LE_1LC0RF_0LD1RD) ===")
m56 = "1RB0RB_1RC1RG_1LD---_1RA1LE_0RF0LE_1LC0RF_0LD1RD"
for l in trace(m56, ['L','E','-','1','0','1','0','1','0','-'], 500000, 30):
    print(" ", l)
print("Follow from last K of m56:")
for l in follow(m56, ['L','E','-','1','0','1','0','1','0','-'], [1,2,1,3,0,3], 0, 3, 500000, 15):
    print(" ", l)
