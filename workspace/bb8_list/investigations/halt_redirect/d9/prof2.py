import sys, threading, cProfile, pstats, io, time
sys.path.insert(0, '.')
import d9f
sys.setrecursionlimit(400000); threading.stack_size(255*1024*1024)
def go():
    pr = cProfile.Profile(); pr.enable()
    t0 = time.time()
    d9f.follow('1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LH_---0LB', 2565, 19, 'look', 1, 300, 80, 10**9, 0, lambda s: None)
    pr.disable()
    s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('tottime').print_stats(18); print(time.time()-t0); print(s.getvalue())
th = threading.Thread(target=go); th.start(); th.join()
