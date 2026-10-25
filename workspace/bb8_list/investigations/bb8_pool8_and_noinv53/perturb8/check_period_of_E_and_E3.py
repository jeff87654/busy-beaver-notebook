import sys
BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from evaluate_ext9_cls53 import parents, kl, run_from_k

tm = "1RB1RA_0LC0LF_1RD1LC_1LE1RE_1LB0RG_0LH1LF_1LG0RA_0RD0LI_---0RB"
p = parents["cls53_09_f"]
t = kl.tmpl(tm, p['tmpl_str'])
B0 = p['B0']

halts = []
rebuilds = {}
for a in range(1, 80):
    er = run_from_k(tm, t, [], a, B0, req_B0=B0)
    if er[0] == 'H':
        halts.append(a)
    elif er[0] == 'K':
        ds, ao, _ = er[1]
        rebuilds[a] = (len(ds), ds[:3], ds[-2:], ao)

print("Halting values of a in E(a) for a=1..79:", halts)
print("Differences between consecutive halting values:", [halts[i+1]-halts[i] for i in range(len(halts)-1)])
for a in range(1, 45):
    if a in halts:
        print(f"  E({a:2d}) [a%9={a%9}, a%18={a%18:2d}]: HALT")
    else:
        l, pfx, sfx, ao = rebuilds[a]
        print(f"  E({a:2d}) [a%9={a%9}, a%18={a%18:2d}]: K len={l:2d} a_out={ao:2d} pfx={pfx} sfx={sfx}")
