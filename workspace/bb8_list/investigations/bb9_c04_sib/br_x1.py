import sys, ctypes, time
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
exec(open('backref_s.py').read().split("if __name__ == '__main__' and sys.argv[1] == '--list'")[0])
for m in ['1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_0RG1LD_1RH1LG_1LC0RG_---0RA','1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0RF','1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---1RA','1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_0RG1LD_1RH1LG_1LC0RG_---1LA']:
    for d in (20, 30, 40):
        t=time.time(); r=check(m, d)
        print(m, d, r, '%.0fs'%(time.time()-t), flush=True)
        if 'UNREACH' in str(r): break
