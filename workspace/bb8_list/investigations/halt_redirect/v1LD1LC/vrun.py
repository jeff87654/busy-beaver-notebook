"""verbose follower for the 1LD1LC machine (family GH) via ord_run.follow"""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import ord_run
ap = argparse.ArgumentParser()
ap.add_argument('--policy', default='std'); ap.add_argument('--bigk', type=int, default=1)
ap.add_argument('--b0', type=int, default=6); ap.add_argument('--stages', type=int, default=80)
ap.add_argument('--maxs', type=int, default=1_000_000_000); ap.add_argument('--log', required=True)
ap.add_argument('--machine', default='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_1LD1LC'); ap.add_argument('--fam', default='GH')
a = ap.parse_args()
lf = open(a.log, 'w')
def log(s):
    lf.write(s + '\n'); lf.flush()
r = ord_run.follow(a.b0, a.policy, a.stages, a.maxs, a.bigk, log=log, FAM=a.fam, M=a.machine)
log('RESULT ' + r); print(a.policy, a.bigk, a.b0, r)
