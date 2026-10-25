import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

# Let's derive the exact 1-decrement atomic step for G#23 and G#24 by checking what runs.back() is when b != 0!
# In step7z_solve_bl1.py, why did trace_runs.exe not print anything on G#23 [10]; 1?
# Because in trace_runs.cpp:
#   long long off = size/2, lo = 0, hi = (long long)w0.size()-1, pos = (long long)w0.size();
# Look! lo was initialized to 0 instead of off! And hi was initialized to w0.size()-1 instead of 0 (relative to T = tp.data() + off)!
# In trace_runs.cpp, T = tp.data() + off, so T[0 .. w0.size()-1] has w0, which means lo = 0, hi = w0.size()-1 IS right, EXCEPT:
# What is pos in kmap2.cpp?! Let's check kmap2.cpp in FW1_DIR!
with open(os.path.join(FW1_DIR, "kmap2.cpp")) as f:
    print(f.read()[:2500])
