import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

tm_rebE2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_rebE2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
T = kl.tmpl(tm_rebE2, t_rebE2)

for ds in [[2, 0], [4, 0], [2], [1], [0]]:
    evs = kl.run(tm_rebE2, ds, 3, 1, steps=50000, nchg=0, maxl=20, T=T, pall=1)
    print(f"K({short(ds):4s}; 3; 1) -> {[e for e in evs[1:] if e[0] in ('K','H')][:4]}")
