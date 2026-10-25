"""st.py MACHINE "tokens" ["tokens" ...] [--far BITS]: one literal stage each (stage13), prints output + slots read"""
import sys, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/g6')
import g6lib
ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('cfgs', nargs='+'); ap.add_argument('--far', default='')
ap.add_argument('--maxs', type=int, default=2_000_000_000)
a = ap.parse_args()
for c in a.cfgs:
    out, used = g6lib.stage(a.machine, c, a.far, a.maxs)
    print(f'[{c}] -> {g6lib.fmt(out)}   slots={" ".join(used)}')
